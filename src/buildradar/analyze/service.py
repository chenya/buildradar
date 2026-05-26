import asyncio
import random
import uuid
from datetime import UTC, datetime

from .schemas import LogAnalysisResponse


def parse_log(raw: str) -> LogAnalysisResponse:
    analyze_log_1 = {
        "format": "jenkins",
        "errors": [
            "[Build] error[E0499]: cannot borrow `x` as mutable more than once",
            "[Build] Build step 'Execute shell' marked build as failure",
            "[Build] Script exited with code 1",
        ],
        "warnings": ["[Build] [WARNING] 3 deprecation warnings emitted"],
        "duration_seconds": 17.0,
        "severity_score": 83,
        "outcome": "Failure",
        "test_summary": {"passed": 7, "failed": 3, "skipped": 0},
    }

    analyze_log_2 = {
        "format": "jenkins",
        "errors": [
            "error: unresolved reference: userServise",
            "[Build Step: Compile] Exit code 1",
            "[Test] AuthServiceTest.testLogin: Expected 200 but was 401 — AssertionError: Expected 200 but was 401",
        ],
        "warnings": [],
        "duration_seconds": 8.0,
        "severity_score": 71,
        "outcome": "Failure",
        "test_summary": {"passed": 1, "failed": 1, "skipped": 0},
    }

    analyze_log_3 = {
        "format": "jenkins",
        "errors": [
            "[Build] src/services/AuthService.ts(84,12): error TS2339: Property 'refreshToken' does not exist on type 'User'",
            "[Build] src/services/AuthService.ts(91,8): error TS2345: Argument of type 'string | undefined' is not assignable to parameter of type 'string'",
            "[Build] src/controllers/UserController.ts(201,5): error TS7006: Parameter 'req' implicitly has an 'any' type",
            "[Build] src/controllers/UserController.ts(210,12): error TS2532: Object is possibly 'undefined'",
            "[Build] TypeScript compilation failed with 4 errors",
            "[Build] Script exited with code 2",
            "[Test] should reject invalid password: Expected status 401 but received 200",
            "[Test] should handle expired token: Expected error TokenExpiredError but received undefined",
        ],
        "warnings": [
            "[Install Dependencies] npm warn deprecated inflight@1.0.6: This module is not supported",
            "[Install Dependencies] npm warn deprecated glob@7.2.3: Glob versions prior to v9 are no longer supported",
        ],
        "duration_seconds": 14.0,
        "severity_score": 86,
        "outcome": "Failure",
        "test_summary": {"passed": 1, "failed": 2, "skipped": 0},
    }

    analyze_log_4 = {
        "format": "jenkins",
        "errors": [
            "[Build] /var/jenkins/workspace/auth-service/src/Services/UserService.cs(42,17): error CS0246: The type or namespace name 'IUserRepository' could not be found (are you missing a using directive or an assembly reference?) [/var/jenkins/workspace/auth-service/src/AuthService.csproj]",
            "[Build] /var/jenkins/workspace/auth-service/src/Services/UserService.cs(67,29): error CS1061: 'UserRepository' does not contain a definition for 'FindByEmailAsync' and no accessible extension method 'FindByEmailAsync' accepting a first argument of type 'UserRepository' could be found [/var/jenkins/workspace/auth-service/src/AuthService.csproj]",
            "[Build] /var/jenkins/workspace/auth-service/src/Controllers/AuthController.cs(103,13): error CS0103: The name 'HashingService' does not exist in the current context [/var/jenkins/workspace/auth-service/src/AuthService.csproj]",
            "[Build] /var/jenkins/workspace/auth-service/src/Controllers/AuthController.cs(118,45): error CS8602: Dereference of a possibly null reference. [/var/jenkins/workspace/auth-service/src/AuthService.csproj]",
            "[Build] Script exited with code 1",
            "[Test] AuthService.Tests.UserServiceTests.GetUser_ShouldReturnNull_WhenUserNotFound: Assert.AreEqual failed. Expected:<null> Actual:<UserNotFoundResult>\n    at AuthService.Tests.UserServiceTests.GetUser_ShouldReturnNull_WhenUserNotFound() in /var/jenkins/workspace/auth-service/src/AuthService.Tests/UserServiceTests.cs:line 87",
            "[Test] AuthService.Tests.AuthControllerTests.Login_ShouldReturn401_WhenPasswordInvalid: Assert.AreEqual failed. Expected:<401> Actual:<200>\n    at AuthService.Tests.AuthControllerTests.Login_ShouldReturn401_WhenPasswordInvalid() in /var/jenkins/workspace/auth-service/src/AuthService.Tests/AuthControllerTests.cs:line 54",
        ],
        "warnings": [
            '[Build] warning MSB3277: Found conflicts between different versions of "Newtonsoft.Json" that could not be resolved.',
            '[Build] warning MSB3277: Found conflicts between different versions of "Microsoft.Extensions.Logging" that could not be resolved.',
        ],
        "duration_seconds": 25.0,
        "severity_score": 92,
        "outcome": "Failure",
        "test_summary": {"passed": 14, "failed": 2, "skipped": 1},
    }

    analyze_log_5 = {
        "format": "jenkins",
        "errors": [
            "[Build] rake aborted!\nLoadError: cannot load such file -- webpacker\n/var/jenkins/workspace/auth-service/config/application.rb:12:in `require'\n/var/jenkins/workspace/auth-service/config/application.rb:12:in `<top (required)>'\n/var/jenkins/workspace/auth-service/Rakefile:5:in `require'\n/var/jenkins/workspace/auth-service/Rakefile:5:in `<main>'",
            "[Build] Script exited with code 1",
            "[Test] UserService#authenticate returns JWT when credentials are valid: expected: 200 got: 401 — ./spec/services/user_service_spec.rb:34",
            "[Test] AuthController#login returns 401 when password is invalid: expected: 401 got: 200 — ./spec/services/auth_controller_spec.rb:58",
            "[Test] UserService#find_by_email raises UserNotFoundError when user does not exist: NameError: uninitialized constant UserNotFoundError — ./app/services/user_service.rb:89",
            "[Test] TokenService#validate raises error on expired token: ArgumentError: wrong number of arguments (given 1, expected 0) — ./app/services/token_service.rb:23",
        ],
        "warnings": [
            "[Install Dependencies] warning: parser gem 3.2.2 is deprecated, use 3.3.0 or higher",
            "[Install Dependencies] warning: gem 'activesupport' 6.1.7 has known security vulnerability CVE-2023-22796",
        ],
        "duration_seconds": 22.0,
        "severity_score": 82,
        "outcome": "Failure",
        "test_summary": {"passed": 19, "failed": 4, "skipped": 2},
    }

    analyze_log_6 = {
        "format": "jenkins",
        "errors": [
            "[Build] /var/jenkins/workspace/auth-service/src/services/UserService.cpp:42:17: error: 'IUserRepository' was not declared in this scope\n   42 |     IUserRepository* repo = new UserRepository();\n      |                 ^~~~~~~~~~~~~~~\n      |                 UserRepository",
            "[Build] /var/jenkins/workspace/auth-service/src/services/UserService.cpp:67:29: error: 'class UserRepository' has no member named 'findByEmail'\n   67 |     auto user = repo->findByEmail(email);\n      |                             ^~~~~~~~~~~",
            "[Build] /var/jenkins/workspace/auth-service/src/controllers/AuthController.cpp:103:13: error: 'HashingService' was not declared in this scope\n  103 |     HashingService hasher;\n      |             ^~~~~~~~~~~~~~",
            "[Build] /var/jenkins/workspace/auth-service/src/utils/TokenUtils.cpp:89:5: error: no matching function for call to 'jwt::create()'\n   89 |     return jwt::create()\n      |            ^~~~~~~~~~~~",
            "[Build] Script exited with code 2",
            "[Test] UserServiceTest.GetUser_ReturnsNullWhenNotFound: Expected equality of these values: result Which is: nullptr — /var/jenkins/workspace/auth-service/tests/UserServiceTest.cpp:54",
            "[Test] AuthControllerTest.Login_Returns401WhenPasswordInvalid: Expected equality of these values: response.status_code() Which is: 200 expected: 401 — /var/jenkins/workspace/auth-service/tests/AuthControllerTest.cpp:87",
            "[Test] Script exited with code 8",
        ],
        "warnings": [
            "[Configure] CMake Warning (dev) at CMakeLists.txt:14 (cmake_minimum_required): Compatibility with CMake < 3.5 will be removed from a future version of CMake.",
            '[Configure] CMake Warning at CMakeLists.txt:67 (find_package): Could not find a configuration file for package "OpenSSL" that is compatible with requested version "3.0".',
            "[Build] /var/jenkins/workspace/auth-service/src/controllers/AuthController.cpp:118:45: warning: dereference of a possibly null pointer [-Wnull-dereference]",
        ],
        "duration_seconds": 26.0,
        "severity_score": 80,
        "outcome": "Failure",
        "test_summary": {"passed": 2, "failed": 2, "skipped": 0},
    }

    analyze_log_7 = {
        "format": "jenkins",
        "errors": [
            "[Build] auth-service/internal/services/user_service.go:42:17: undefined: IUserRepository",
            "[Build] auth-service/internal/services/user_service.go:67:16: repo.FindByEmail undefined (type *UserRepository has no field or method FindByEmail)",
            "[Build] auth-service/internal/controllers/auth_controller.go:103:2: undefined: HashingService",
            "[Build] auth-service/internal/controllers/auth_controller.go:118:14: invalid operation: cannot indirect response (variable of type string)",
            "[Build] auth-service/internal/utils/token_utils.go:23:9: cannot use token (variable of type Token) as type string in argument to jwt.Parse",
            "[Build] Script exited with code 1",
            '[Test] TestUserService_GetUser_ReturnsNullWhenNotFound (0.34s): Error: Not equal\n    expected: nil\n    actual  : &UserNotFoundResult{ID:0, Message:"user not found"}\n    Diff:\n    --- Expected\n    +++ Actual\n    @@ -1 +1,4 @@\n    -<nil>\n    +&UserNotFoundResult{\n    +  ID: 0,\n    +  Message: "user not found",\n    +}',
            "[Test] TestAuthController_Login_Returns401WhenPasswordInvalid (0.18s): Error: Not equal\n    expected: 401\n    actual  : 200",
        ],
        "warnings": [
            "[Lint] auth-service/internal/services/user_service.go:34:5: ST1003: should not use underscores in Go names; func get_user should be getUser (stylecheck)",
            "[Lint] auth-service/internal/services/user_service.go:89:12: errcheck: Error return value of `repo.Save` is not checked (errcheck)",
            "[Lint] auth-service/internal/controllers/auth_controller.go:56:9: ineffassign: ineffectual assignment to `err` (ineffassign)",
            "[Lint] WARN golangci-lint took 3.2s — consider adding a .golangci.yml timeout setting",
        ],
        "duration_seconds": 22.0,
        "severity_score": 79,
        "outcome": "Failure",
        "test_summary": {"passed": 3, "failed": 2, "skipped": 0},
    }

    analyze_logs = [
        analyze_log_1,
        analyze_log_2,
        analyze_log_3,
        analyze_log_4,
        analyze_log_5,
        analyze_log_6,
        analyze_log_7,
    ]

    random_log = random.choice(analyze_logs)
    random_log["analysis_id"] = ""
    random_log["analyzed_at"] = ""
    return LogAnalysisResponse(**random_log)


class AnalyzeService:
    async def analyze(self, raw: str) -> LogAnalysisResponse:
        # fmt = detect_format(raw)
        fmt = "jenkins"
        # parsed = await asyncio.to_thread(
        #     logmill.parse_teamcity_log if fmt == "teamcity"
        #     else logmill.parse_jenkins_log,
        #     raw,
        # )
        parsed = await asyncio.to_thread(parse_log, raw)

        return LogAnalysisResponse(
            analysis_id=str(uuid.uuid4()),
            analyzed_at=datetime.now(UTC).isoformat(),
            format=fmt,
            errors=parsed.errors,
            warnings=parsed.warnings,
            duration_seconds=parsed.duration_seconds,
            severity_score=parsed.severity_score,
            outcome=str(parsed.outcome) if parsed.outcome else None,
            test_summary=parsed.test_summary,
        )
