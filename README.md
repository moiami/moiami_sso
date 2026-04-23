# SSO сервис moiami

1. POST /api/v1/auth/login
2. POST /api/v1/auth/validate
3. POST /api/v1/auth/refresh
4. POST /api/v1/auth/register 
5. GET /api/v1/roles/roles
6. GET /api/v1/roles/role
7. POST /api/v1/roles/create_role
8. PATCH /api/v1/roles/update_role
9. DELETE /api/v1/roles/delete_role
10. GET /api/v1/user/users
11. GET /api/v1/user/user
12. POST /api/v1/user/change_role
13. DELETE /api/v1/user/delete_user

<pre>
    moiami_sso/                 
    ├── .dockerignore           
    ├── .gitignore              
    ├── .python-version         
    ├── docker-compose.yaml     
    ├── Dockerfile              
    ├── entrypoint.sh           
    ├── pyproject.toml          
    ├── uv.lock                 
    ├── README.md               
    │
    └── src/                    
        ├── alembic.ini         
        ├── constants.py        
        ├── main.py             
        ├── __init__.py
        │
        ├── api/                
        │   ├── __init__.py
        │   └── routers/        
        │       ├── auth_router.py    
        │       ├── role_router.py    
        │       ├── user_router.py    
        │       └── __init__.py
        │
        ├── data/               
        │   ├── __init__.py
        │   │
        │   ├── models/         
        │   │   ├── base.py     
        │   │   ├── role.py
        │   │   ├── token.py
        │   │   ├── user.py
        │   │   ├── user_role.py 
        │   │   └── __init__.py
        │   │
        │   ├── repositories/   
        │   │   ├── auth_repository.py
        │   │   ├── role_repository.py
        │   │   ├── user_repository.py
        │   │   └── __init__.py
        │   │
        │   └── schemas/        
        │       ├── role.py
        │       ├── user.py
        │       └── __init__.py
        │
        ├── migrations/         
        │   ├── env.py
        │   ├── README
        │   ├── script.py.mako
        │   └── versions/
        │       └── 319e3f7e0a6c_.py 
        │
        └── services/           
            ├── role_service.py
            ├── security_service.py
            ├── user_service.py
            └── __init__.py
</pre>