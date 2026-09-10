<Context>
    <Philosophy>
        This project is not merely an application; it is a rigid academic framework designed to enforce software engineering mastery.
        It rejects "easy" solutions in favor of "correct" solutions.
        The primary objective is to internalize SOLID principles, strict OOP, and modular Clean Architecture.

        We prioritize:
        1. Maintainability over Speed.
        2. Explicitness over "Magic".
        3. Interfaces over Implementation.
    </Philosophy>
    <Scope>
        A full-stack enterprise application orchestrating a Python FastAPI backend and an Angular (Modern) frontend.
        The system mimics a high-scale environment where code readability, testability, and decoupling are paramount.
    </Scope>
    <Actors>
        - The Architect (You): Defines the contracts (Interfaces/ABCs).
        - The Builder (You): Implements the logic behind the contracts.
        - The Consumer (You): Consumes the logic via strictly typed APIs and ViewModels.
    </Actors>
</Context>

<Architecture>
    <Backend_Pattern>
        CLEAN ARCHITECTURE (Onion Architecture)

        [ External Request ]
               ⬇
        [ Interface Layer ] -> (Routers, CLI)
               ⬇
        [ Application Layer ] -> (Use Cases, Services, DTOs)
               ⬇
        [ Domain Layer ] -> (Entities, Interface Definitions/ABCs)
               ⬆
        [ Infrastructure Layer ] -> (DB Implementations, 3rd Party APIs)
    </Backend_Pattern>

    <Frontend_Pattern>
        MVVM (Model-View-ViewModel) + SIGNAL ARCHITECTURE

        [ View (Template) ]
               ⬇ (Triggers Action)
        [ ViewModel (Component) ] -> Holds State (Signals), Handles UI Logic
               ⬇ (Calls)
        [ Model (Service/Repository) ] -> Handles HTTP, Data Transformation
               ⬇ (Returns Observable/Signal)
        [ View (Template) ] -> Updates via Signal bindings (No manual change detection)
    </Frontend_Pattern>

    <CICD_Pipeline>
        CI/CD is implemented via GitHub Actions in .github/workflows/

        CI (.github/workflows/ci.yml) — runs on every PR and push to main/develop:
            - lint:              ruff check + ruff format --check (fast, no Docker)
            - type-check:        mypy --ignore-missing-imports (advisory)
            - unit-tests:        pytest -m unit --cov (fast, no Docker, blocks merge)
            - integration-tests: pytest -m integration (testcontainers/Docker)
            - e2e-tests:         pytest -m e2e (testcontainers/Docker)
            - docker-build:      validates Dockerfile builds (gated on lint + unit)
            - frontend-lint:     ng lint / eslint (fast, no Docker)
            - frontend-tests:    ng test --watch=false (fast, no Docker)

        CD (.github/workflows/cd.yml) — runs on push to main and on GitHub Release:
            - build-and-push: Multi-arch Docker image (linux/amd64, linux/arm64) → GHCR (backend + frontend images)
            - deploy-staging:    Triggered on push to main → staging environment
            - deploy-production: Triggered on GitHub Release → production environment

        Image registry: ghcr.io (GitHub Container Registry, uses GITHUB_TOKEN — no extra secrets)
        Image tags: sha-<short>, branch name, semver (on release), latest (on main)
    </CICD_Pipeline>
</Architecture>

<Requirements>
    <Backend_Tech_Stack>
        - Language: Python 3.11+
        - Framework: FastAPI (strictly for routing only)
        - Validation: Pydantic V2 (Strict Mode)
        - DI Framework: Native FastAPI Depends or specialized container (e.g., Dependency Injector)
        - Logging: Structlog (JSON format, context-aware)
        - Testing: Pytest (100% coverage on Domain/Application layers)
    </Backend_Tech_Stack>

    <Frontend_Tech_Stack>
        - Framework: Angular v21+ (Standalone Components, Signals)
        - Styling: SCSS (Strict BEM or Modular), Design Tokens
        - State: Signals (Native) + RxJS (for complex streams only)
        - HTTP: HttpClient with Interceptors for Logging/Auth
    </Frontend_Tech_Stack>

    <Database_Infrastructure>
        - Database: PostgreSQL
        - Migration: Alembic
        - Strategy: SQL-First, migrations reviewed before merge. No ORM auto-generation trusted blindly.
        - Driver: AsyncPG / SQLAlchemy (Async)
    </Database_Infrastructure>
</Requirements>

<Constraints>
    <DO>
        <Universal>
            - DO ensure every single class has a Single Responsibility (SRP).
            - DO document every public method with Docstrings (Python) or JSDoc (TS).
        </Universal>

        <Backend>
            - DO define an Abstract Base Class (ABC) for *every* Repository.
            - DO inject dependencies via `__init__` in Services.
            - DO map all Database Exceptions to Domain Exceptions before they reach the Router.
            - DO use `UPPER_CASE` for global constants and configuration.
            - DO implement a global Exception Handler that returns standardized JSON error responses.
        </Backend>

        <Frontend>
            - DO create a "Design System" folder first (`src/app/theme`) containing:
                - `colors.ts` (CONSTANTS only)
                - `typography.scss` (Mixins)
                - `icons.registry.ts` (SVG definitions)
            - DO use Angular Signals (`computed`, `effect`) for all derived state.
            - DO decouple Components from API logic entirely (The Component should not know what HTTP is).
            - DO use "Smart" (Container) vs "Dumb" (Presentational) component patterns.
        </Frontend>
    </DO>

    <DO_NOT>
        <Backend>
            - DO NOT put business logic in `api/routes`. Routers are for parsing Request -> DTO only.
            - DO NOT expose ORM Entities (SQLAlchemy Models) to the outside world. Always map to Pydantic Response DTOs.
            - DO NOT use global variables for state.
            - DO NOT import `Infrastructure` modules into `Domain` modules. (Circular Dependency / Architectural Violation).
        </Backend>

        <Frontend>
            - DO NOT write logic inside the HTML Template (e.g., `{{ data.filter(...) }}`). Compute it in the ViewModel.
            - DO NOT use `any`. Ever. Use `unknown` if strictly necessary, but prefer defined Interfaces.
            - DO NOT hardcode colors (e.g., `#FFFFFF`) in Component SCSS. Use CSS Variables/Design Tokens.
            - DO NOT import from `app.module` (Standalone components are mandatory).
        </Frontend>

        <Database>
            - DO NOT modify the database schema manually. If it's not in an Alembic revision file, it doesn't exist.
        </Database>
    </DO_NOT>

    <SUCCESS_METRICS>
        1. "The Swap Test": Can you swap the PostgreSQL implementation with a MongoDB implementation by changing ONLY the Infrastructure layer and DI config?
        2. "The Junior Test": Can a junior developer read the `Domain` folder and understand exactly what the business does without seeing a single line of SQL or HTTP code?
        3. "The Reskin Test": Can you change the entire color scheme of the app by modifying only `variables.scss`?
    </SUCCESS_METRICS>
</Constraints>

<Coding_Styles>
    <Python>
        <Naming>
            - Classes: `PascalCase` (e.g., `UserProfileService`)
            - Variables/Functions: `snake_case` (e.g., `get_product_by_id`)
            - Interfaces: Prefixed with I (e.g., `IProductRepository`) - *Optional but recommended for clarity in this strict environment.*
            - Private members: `_prefixed` (e.g., `_validate_email`)
        </Naming>
        <Formatting>
            - Tools: `Ruff` (Linter), `Black` (Formatter), `MyPy` (Type Checker).
            - Rules: Line length 88-100. Double quotes.
        </Formatting>
    </Python>

    <Angular_TypeScript>
        <Naming>
            - Files: `kebab-case` (e.g., `user-profile.component.ts`)
            - Classes: `PascalCase` (e.g., `UserProfileComponent`)
            - Observables: Suffix with `$` (e.g., `users$`)
            - Signals: No specific suffix, but prefer noun phrases (e.g., `currentUser`)
        </Naming>
        <Formatting>
            - Tools: `Prettier`, `ESLint`.
            - Rules: Single quotes. 2 Space indentation.
        </Formatting>
        <Example_Good>
            ```typescript
            @Component({ ... })
            export class UserListComponent {
                // Dependency Injection
                private userService = inject(UserService);

                // State (Signal)
                users = this.userService.getUsers();

                // Computed State
                userCount = computed(() => this.users().length);
            }
            ```
        </Example_Good>
    </Angular_TypeScript>

    <SQL>
        <Naming>
            - Tables: `snake_case`, plural (e.g., `products`, `orders`)
            - Keys: `pk_table_name`, `fk_source_target`
        </Naming>
        <Keywords>
            - ALWAYS UPPERCASE (e.g., `SELECT * FROM products WHERE id = 1;`)
        </Keywords>
    </SQL>
</Coding_Styles>

<Workflow>
    <New_Feature_Checklist>
        1. **Domain:** Define the Data Models (Entities) and Repository Interfaces (ABCs).
        2. **Application:** Create the Service class implementing the business logic. Define Pydantic DTOs for input/output.
        3. **Infrastructure:** Implement the Repository Interface using SQL/ORM.
        4. **Interface (API):** Create the Router, wire the Service (DI), and map Request -> DTO -> Service.
        5. **Frontend (Model):** Define TypeScript Interface matching the API Response DTO.
        6. **Frontend (Service):** Add method to Data Service.
        7. **Frontend (View/ViewModel):** Build Component using Signals.
        8. **Tests:** Unit tests for the service (mock repos), integration test for the repo, e2e test for the router.
    </New_Feature_Checklist>

    <Developer_Commands>
        Use `make help` to list all commands.

        Code quality (run before every commit):
            make lint          → ruff check (mirrors CI lint job)
            make format        → ruff format --fix (auto-fix style issues)
            make type-check    → mypy static analysis

        Testing:
            make unit          → fast unit tests, no Docker needed
            make integration   → integration tests, requires Docker daemon
            make e2e           → E2E HTTP tests, requires Docker daemon
            make coverage      → unit tests + HTML coverage report

        Docker:
            make build         → build Docker image locally
            make up            → start app + postgres + frontend via docker compose
            make down          → stop and remove containers + volumes
            make logs          → tail app container logs
            make shell         → interactive shell in the running app container
    </Developer_Commands>

    <Frontend_Developer_Commands>
        NOTE: verify these against the actual scripts in frontend/package.json and adjust as needed.

            ng serve           → run dev server with live reload
            ng lint            → eslint check (mirrors CI frontend-lint job)
            ng test            → run unit tests (Karma/Jasmine or Jest, watch mode)
            ng test --watch=false --browsers=ChromeHeadless → CI-style single run
            ng build --configuration production → production build
    </Frontend_Developer_Commands>

    <CI_Rules>
        - DO NOT push code that fails `make lint` or `make unit`.
        - DO mark every backend test with the correct pytest marker: @pytest.mark.unit, @pytest.mark.integration, or @pytest.mark.e2e.
        - DO inject the abstract repository in unit tests, use db session in integration tests, and use client in e2e tests.
        - DO keep integration tests focused on the repository layer only (no HTTP, no service logic).
        - DO keep e2e tests focused on HTTP contract verification (status codes, response shape, auth enforcement).
        - DO NOT introduce Docker dependencies in unit tests.
        - The CI coverage gate is currently set to 80% for the unit suite. The long-term goal is 100% on Domain + Application layers.
        - DO NOT push frontend code that fails `ng lint` or `ng test`.
    </CI_Rules>
</Workflow>