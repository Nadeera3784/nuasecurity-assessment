## Technical Assessment(Backend + Frontend)

This repository contains a complete take‑home assignment:
- Backend: Django + DRF + Neo4j graph database (Admin/Supplier, groceries, items, daily income)
- Frontend: Next.js + shadcn/ui implementing the Figma design and table interactions

### Tech
- Backend: Django, DRF, neomodel (Neo4j)
- Frontend: Next.js, shadcn/ui, TypeScript
- Tooling: Docker Compose, JWT auth, GitHub Actions CI

### Quick start (Docker)
```bash
git clone <repository-url>
cd nuasecurity
docker compose up -d --build
```

Services:
- Frontend: http://localhost:3000
- API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/
- Neo4j Browser: http://localhost:7474 (neo4j/password)

### Credentials
- Django admin superuser is created by the startup commands (see docker-compose). If missing, run inside backend container:
```bash
python manage.py createsuperuser
```

### What’s implemented (Backend)
- Admin can create/update/soft-delete groceries, create/manage suppliers, manage items/prices, and read daily income
- Supplier can add items and daily income for their assigned grocery; can read items globally but only modify own-grocery items
- JWT authentication required for all actions; `created_at`/`updated_at` maintained; item delete is soft delete
- Django Admin UI:
  - Add/Edit/Delete for Admins, Suppliers, Groceries, Items; Daily Income dashboard with per-day totals
  - Supplier login sees only Items and Daily Income, scoped to their grocery; archived badge for soft-deleted items
- Tests: DRF API tests covering auth, permissions, soft delete, and totals. Run with Neo4j in Docker

Run backend tests (locally):
```bash
cd backend
NEO4J_BOLT_URL=bolt://neo4j:password@localhost:7687 python manage.py test api.tests --verbosity 2
```

### What’s implemented (Frontend)
- Figma parity screens using shadcn/ui components
- Assets table interactions:
  - Add/remove assets inline
  - Prevent duplicate asset identifiers
  - Asset type: WEB/MOBILE; Bounty eligibility: ELIGIBLE/INELIGIBLE
  - Submit persists row to the table

### For a fully functional frontend implementation with PostgreSQL integration, please refer to the following  [link](https://github.com/Nadeera3784/intigriti) .

### CI
GitHub Actions workflow validates both projects on push/PR (lint, build, backend tests against Neo4j).

### Next steps (if given more time)
- API docs via drf-spectacular
- Learn more advance acess pattern with Neo4j
- Query optimizations

- More negative tests (validation edge cases)
- Admin UI improvement  
- Admin logic to seperate user level 
- Build entire database with Neo4j currenty it's hybrid due to lack of experience with Neo4j


