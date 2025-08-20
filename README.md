# Frontend

The frontend is built with Next.js and leverages local storage for data persistence.

## Technologies
1. Nextjs 
2. shadcn/ui
3. Any other libraries, framework might help you.

### Instructions
1. Look at the figma design link in the links section.
2. Analyze the UI carefully.
3. Reflect the prepared design in figma into nextjs application.
4. Asset you want to test field has two values which are WEB and MOBILE
5. Bounty eligibility field has two options which are ELIGIBLE and INELIGIBLE
6. When click on add button, it should a new asset to the program and when click on delete, it should be deleted from the assets list.
7. If there is already an asset identifier, do not duplicate it.
8. When click on submit, add the new information in the table.


## Local Setup

### Clone the Repository

```bash
git clone <repository-url>
```

### Start the docker

```bash
docker compose up -d --build
```
The application will be available at `http://localhost:3000`

## For a fully functional frontend implementation with PostgreSQL integration, please refer to the followin  [link](https://github.com/Nadeera3784/intigriti) .


# Backend

There is a new grocery company that want to create a system that will track each grocery branch that belongs to it by managing the grocery, items, the person in charge of the grocery, and the daily income. The system details is in the requirements section.

## Technologies
1. Django
2. Django rest framework
3. Graph database (neo4j)

## Requirements
There are two users in the system.

## Admin
1. Create a new grocery account.
2. Create a new grocery responsible user account.
3. Manage the grocery by editing, deleting both accounts.
4. Manage the items of each grocery with their prices.
5. Read the daily income of each grocery.

## Grocery responsible user (Supplier)
1. Add new items to the grocery.
2. Add the daily income of the grocery.

## Required fields
1. admin & supplier name
2. admin & supplier email
3. admin & supplier password.
4. create at
5. update at
6. grocery name
7. grocery location
8. item name
9. item type (ex: food, game, etc.
10. item location (ex: first roof, second roof, etc)
11. daily income

## Constraints
1. Any action in the system needs an authentication.
2. A supplier cannot add, edit, delete any item in another grocery.
3. A supplier can read other groceries items.
4. Any action will is implemented, the update at will be modified.
5. The delete action should not delete the item from the whole db, it should soft delete it.



## Local Setup

### Clone the Repository

```bash
git clone <repository-url>
```

### Start the docker

```bash
docker compose up -d --build
```

Django Admin: http://localhost:8000/admin/ (admin/admin123)

API: http://localhost:8000/api/

Neo4j Browser: http://localhost:7474 (neo4j/password)