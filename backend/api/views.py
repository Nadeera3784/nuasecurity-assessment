from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from .models import Admin, Supplier, Grocery, Item, DailyIncome, User
from .serializers import (
    AdminRegistrationSerializer,
    SupplierRegistrationSerializer,
    UserSerializer,
    LoginSerializer,
    GrocerySerializer,
    ItemSerializer,
    DailyIncomeSerializer,
    GroceryDetailSerializer,
)
from .permissions import (
    IsAdmin,
    IsAdminOrSupplier,
    IsSupplierOwnerOrAdmin,
    CanReadItems,
)
from .authentication import create_jwt_token


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


@api_view(["POST"])
@permission_classes([AllowAny])
def register_admin(request):
    serializer = AdminRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        admin = serializer.save()
        tokens = create_jwt_token(admin)
        user_data = UserSerializer(admin).data
        return Response(
            {
                "user": user_data,
                "tokens": tokens,
                "message": "Admin registered successfully",
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAdmin])
def register_supplier(request):
    serializer = SupplierRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        supplier = serializer.save()
        user_data = UserSerializer(supplier).data
        return Response(
            {"user": user_data, "message": "Supplier registered successfully"},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.nodes.get(email=email)
            if user.check_password(password) and user.is_active:
                tokens = create_jwt_token(user)
                user_data = UserSerializer(user).data
                return Response(
                    {
                        "user": user_data,
                        "tokens": tokens,
                        "message": "Login successful",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAdminOrSupplier])
def profile(request):
    """Get user profile"""
    user_data = UserSerializer(request.neo4j_user).data
    return Response({"user": user_data})


class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAdmin]
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        """List all users"""
        users = User.nodes.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get specific user"""
        try:
            user = User.nodes.get(uid=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        try:
            user = User.nodes.get(uid=pk)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                user.name = serializer.validated_data.get("name", user.name)
                user.email = serializer.validated_data.get("email", user.email)
                user.is_active = serializer.validated_data.get(
                    "is_active", user.is_active
                )
                user.save()
                return Response(UserSerializer(user).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        """Soft delete user (Admin only)"""
        try:
            user = User.nodes.get(uid=pk)
            user.is_active = False
            user.save()
            return Response({"message": "User deactivated successfully"})
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class GroceryViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrSupplier]
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        """List groceries"""
        neo4j_user = request.neo4j_user

        if isinstance(neo4j_user, Admin):
            groceries = Grocery.nodes.filter(is_active=True)
        else:
            groceries = Grocery.nodes.filter(is_active=True)

        serializer = GrocerySerializer(groceries, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            grocery = Grocery.nodes.get(uid=pk, is_active=True)
            neo4j_user = request.neo4j_user

            if isinstance(neo4j_user, Supplier):
                supplier_grocery = neo4j_user.responsible_for.single()
                if supplier_grocery and supplier_grocery.uid == grocery.uid:
                    serializer = GroceryDetailSerializer(grocery)
                else:
                    serializer = GrocerySerializer(grocery)
            else:
                serializer = GroceryDetailSerializer(grocery)

            return Response(serializer.data)
        except Grocery.DoesNotExist:
            return Response(
                {"error": "Grocery not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        if not isinstance(request.neo4j_user, Admin):
            return Response(
                {"error": "Only admins can create groceries"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = GrocerySerializer(data=request.data)
        if serializer.is_valid():
            grocery = serializer.save()
            request.neo4j_user.manages_groceries.connect(grocery)
            return Response(
                GrocerySerializer(grocery).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        if not isinstance(request.neo4j_user, Admin):
            return Response(
                {"error": "Only admins can update groceries"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            grocery = Grocery.nodes.get(uid=pk, is_active=True)
            serializer = GrocerySerializer(grocery, data=request.data, partial=True)
            if serializer.is_valid():
                grocery = serializer.save()
                return Response(GrocerySerializer(grocery).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Grocery.DoesNotExist:
            return Response(
                {"error": "Grocery not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        if not isinstance(request.neo4j_user, Admin):
            return Response(
                {"error": "Only admins can delete groceries"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            grocery = Grocery.nodes.get(uid=pk)
            grocery.is_active = False
            grocery.save()
            return Response({"message": "Grocery deactivated successfully"})
        except Grocery.DoesNotExist:
            return Response(
                {"error": "Grocery not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def assign_supplier(self, request, pk=None):
        try:
            grocery = Grocery.nodes.get(uid=pk, is_active=True)
            supplier_id = request.data.get("supplier_id")

            if not supplier_id:
                return Response(
                    {"error": "supplier_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            supplier = Supplier.nodes.get(uid=supplier_id, is_active=True)

            existing_connection = supplier.responsible_for.single()
            if existing_connection:
                supplier.responsible_for.disconnect(existing_connection)

            supplier.responsible_for.connect(grocery)

            return Response({"message": "Supplier assigned successfully"})
        except (Grocery.DoesNotExist, Supplier.DoesNotExist):
            return Response(
                {"error": "Grocery or Supplier not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class ItemViewSet(viewsets.ViewSet):
    permission_classes = [CanReadItems]
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        grocery_id = request.query_params.get("grocery_id")

        if grocery_id:
            try:
                grocery = Grocery.nodes.get(uid=grocery_id, is_active=True)
                items = grocery.items.filter(is_deleted=False)
            except Grocery.DoesNotExist:
                return Response(
                    {"error": "Grocery not found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            items = Item.nodes.filter(is_deleted=False)

        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            item = Item.nodes.get(uid=pk, is_deleted=False)
            serializer = ItemSerializer(item)
            return Response(serializer.data)
        except Item.DoesNotExist:
            return Response(
                {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        neo4j_user = request.neo4j_user
        grocery_id = request.data.get("grocery_id")

        if not grocery_id:
            return Response(
                {"error": "grocery_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            grocery = Grocery.nodes.get(uid=grocery_id, is_active=True)

            if isinstance(neo4j_user, Supplier):
                supplier_grocery = neo4j_user.responsible_for.single()
                if not supplier_grocery or supplier_grocery.uid != grocery.uid:
                    return Response(
                        {"error": "You can only add items to your assigned grocery"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            serializer = ItemSerializer(data=request.data)
            if serializer.is_valid():
                item = serializer.save()
                grocery.items.connect(item)

                if isinstance(neo4j_user, Supplier):
                    neo4j_user.added_items.connect(item)

                return Response(
                    ItemSerializer(item).data, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Grocery.DoesNotExist:
            return Response(
                {"error": "Grocery not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        try:
            item = Item.nodes.get(uid=pk, is_deleted=False)

            if isinstance(request.neo4j_user, Supplier):
                supplier_grocery = request.neo4j_user.responsible_for.single()
                item_grocery = item.belongs_to_grocery.single()
                if (
                    not supplier_grocery
                    or not item_grocery
                    or supplier_grocery.uid != item_grocery.uid
                ):
                    return Response(
                        {"error": "You can only update items in your assigned grocery"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            serializer = ItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                item = serializer.save()
                return Response(ItemSerializer(item).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Item.DoesNotExist:
            return Response(
                {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            item = Item.nodes.get(uid=pk, is_deleted=False)

            if isinstance(request.neo4j_user, Supplier):
                supplier_grocery = request.neo4j_user.responsible_for.single()
                item_grocery = item.belongs_to_grocery.single()
                if (
                    not supplier_grocery
                    or not item_grocery
                    or supplier_grocery.uid != item_grocery.uid
                ):
                    return Response(
                        {"error": "You can only delete items in your assigned grocery"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            item.soft_delete()
            return Response({"message": "Item deleted successfully"})
        except Item.DoesNotExist:
            return Response(
                {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND
            )


class DailyIncomeViewSet(viewsets.ViewSet):
    permission_classes = [IsSupplierOwnerOrAdmin]
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        neo4j_user = request.neo4j_user
        grocery_id = request.query_params.get("grocery_id")

        if isinstance(neo4j_user, Admin):
            if grocery_id:
                try:
                    grocery = Grocery.nodes.get(uid=grocery_id, is_active=True)
                    incomes = grocery.daily_incomes.all()
                except Grocery.DoesNotExist:
                    return Response(
                        {"error": "Grocery not found"}, status=status.HTTP_404_NOT_FOUND
                    )
            else:
                incomes = DailyIncome.nodes.all()
        else:
            supplier_grocery = neo4j_user.responsible_for.single()
            if not supplier_grocery:
                return Response(
                    {"error": "No grocery assigned"}, status=status.HTTP_403_FORBIDDEN
                )
            incomes = supplier_grocery.daily_incomes.all()

        serializer = DailyIncomeSerializer(incomes, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            income = DailyIncome.nodes.get(uid=pk)

            if isinstance(request.neo4j_user, Supplier):
                supplier_grocery = request.neo4j_user.responsible_for.single()
                income_grocery = income.grocery.single()
                if (
                    not supplier_grocery
                    or not income_grocery
                    or supplier_grocery.uid != income_grocery.uid
                ):
                    return Response(
                        {"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN
                    )

            serializer = DailyIncomeSerializer(income)
            return Response(serializer.data)
        except DailyIncome.DoesNotExist:
            return Response(
                {"error": "Income record not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        neo4j_user = request.neo4j_user
        grocery_id = request.data.get("grocery_id")

        if isinstance(neo4j_user, Supplier):
            supplier_grocery = neo4j_user.responsible_for.single()
            if not supplier_grocery:
                return Response(
                    {"error": "No grocery assigned"}, status=status.HTTP_403_FORBIDDEN
                )
            grocery = supplier_grocery
        else:
            # Admin can specify grocery
            if not grocery_id:
                return Response(
                    {"error": "grocery_id is required for admins"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                grocery = Grocery.nodes.get(uid=grocery_id, is_active=True)
            except Grocery.DoesNotExist:
                return Response(
                    {"error": "Grocery not found"}, status=status.HTTP_404_NOT_FOUND
                )

        serializer = DailyIncomeSerializer(data=request.data)
        if serializer.is_valid():
            income = serializer.save()
            grocery.daily_incomes.connect(income)

            if isinstance(neo4j_user, Supplier):
                neo4j_user.recorded_incomes.connect(income)

            return Response(
                DailyIncomeSerializer(income).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
