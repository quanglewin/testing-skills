---
title: Controller Test Rules
impact: HIGH
impactDescription: ensures correct controller unit testing via direct instantiation and precise ActionResult assertions
tags: csharp, tests, controller, aspnetcore, actionresult
---

## Controller Test Rules

Unit test ASP.NET Core controllers by **instantiating them directly** with substituted services and asserting on the returned `ActionResult` types. No web host, no HTTP.

### FORBIDDEN

- **FORBIDDEN** to use `WebApplicationFactory<T>` or `TestServer` in unit tests — that boots the full HTTP pipeline (integration testing, different rule set)

**Incorrect:**

```csharp
// Integration-level setup presented as a unit test
public class UserControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task GetUser_ExistingId_Returns200()
    {
        var client = _factory.CreateClient(); // full pipeline - not a unit test
        var response = await client.GetAsync("/api/users/1");
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }
}
```

**Correct:**

```csharp
using FluentAssertions;
using Microsoft.AspNetCore.Mvc;
using NSubstitute;
using Xunit;

public class UserControllerTests
{
    private readonly IUserService _userService = Substitute.For<IUserService>();
    private readonly UserController _controller;

    public UserControllerTests()
    {
        _controller = new UserController(_userService);
    }

    [Fact]
    public void GetUser_ExistingId_ReturnsOkWithUser()
    {
        // Arrange
        var expectedUser = new User("1", "John", "john@test.com");
        _userService.FindById("1").Returns(expectedUser);

        // Act
        IActionResult actualResult = _controller.GetUser("1");

        // Assert
        User actualUser = actualResult.Should().BeOfType<OkObjectResult>()
            .Which.Value.Should().BeOfType<User>().Subject;
        actualUser.Id.Should().Be("1");
        actualUser.Name.Should().Be("John");
    }

    [Fact]
    public void GetUser_NonExistentId_ReturnsNotFound()
    {
        // Arrange
        _userService.FindById("999").Returns((User?)null);

        // Act
        IActionResult actualResult = _controller.GetUser("999");

        // Assert
        actualResult.Should().BeOfType<NotFoundResult>();
    }

    [Fact]
    public void CreateUser_ValidRequest_ReturnsCreatedAtAction()
    {
        // Arrange
        var request = new CreateUserRequest("John", "john@test.com");
        _userService.Create(Arg.Is<CreateUserRequest>(r => r.Email == "john@test.com"))
            .Returns(new User("1", "John", "john@test.com"));

        // Act
        IActionResult actualResult = _controller.CreateUser(request);

        // Assert
        var actualCreated = actualResult.Should().BeOfType<CreatedAtActionResult>().Subject;
        actualCreated.ActionName.Should().Be(nameof(UserController.GetUser));
        actualCreated.StatusCode.Should().Be(201);
    }

    [Fact]
    public void CreateUser_DuplicateEmail_ReturnsBadRequestWithMessage()
    {
        // Arrange
        var request = new CreateUserRequest("John", "taken@test.com");
        _userService.Create(Arg.Any<CreateUserRequest>())
            .Returns(x => throw new DuplicateEmailException("taken@test.com"));

        // Act
        IActionResult actualResult = _controller.CreateUser(request);

        // Assert
        actualResult.Should().BeOfType<BadRequestObjectResult>()
            .Which.Value.Should().Be("Email already registered: taken@test.com");
    }
}
```

Note on `ActionResult<T>`: when the action returns `ActionResult<T>`, assert on `actualResult.Result` (the wrapped `IActionResult`), e.g. `actualResult.Result.Should().BeOfType<OkObjectResult>()`.

### Separate Tests per Status Code

**Never merge** different 4xx outcomes into one test. Each of 400, 401, 403, 404 (and any other status the controller can return) gets its own test with its own name — a merged test hides which behavior broke.

```csharp
// WRONG - one test asserting "some 4xx happens" for several inputs
// CORRECT - GetUser_NonExistentId_ReturnsNotFound and
//           CreateUser_DuplicateEmail_ReturnsBadRequestWithMessage as separate [Fact]s
```

For 401/403: if the controller method itself returns `Unauthorized()`/`Forbid()`, unit test those branches separately. If auth is enforced only by `[Authorize]` attributes, see the pipeline limitation below — that enforcement is middleware behavior, an integration concern.

### [ApiController] Validation Limitation — Be Honest

With `[ApiController]`, the automatic `400 Bad Request` for invalid models happens in the **MVC pipeline before the action executes**. Calling the action directly in a unit test **bypasses it** — the action runs even with an invalid DTO, and no automatic 400 is produced.

- Do NOT write a unit test that passes an invalid DTO to the action and expects an automatic 400 — it tests nothing real
- Test validation attributes (`[Required]`, `[EmailAddress]`, ranges) separately via `Validator.TryValidateObject` on the DTO, or defer auto-400 behavior to integration tests
- Manual `ModelState` checks inside the action body (`if (!ModelState.IsValid) return BadRequest(ModelState);`) CAN be unit tested by seeding an error first:

```csharp
[Fact]
public void UpdateUser_InvalidModelState_ReturnsBadRequest()
{
    // Arrange - only valid when the action itself checks ModelState
    _controller.ModelState.AddModelError("Email", "Invalid email format");

    // Act
    IActionResult actualResult = _controller.UpdateUser("1", new UpdateUserRequest("", "bad"));

    // Assert
    actualResult.Should().BeOfType<BadRequestObjectResult>();
}
```

### What to Test in Controller Unit Tests

1. **Result type per branch**: `OkObjectResult`, `NotFoundResult`, `BadRequestObjectResult`, `CreatedAtActionResult`, `NoContentResult`
2. **Response payload**: assert fields of `.Value`, not just the type
3. **Status codes**: `((ObjectResult)actualResult).StatusCode.Should().Be(422);` for non-standard results
4. **Service interaction**: the right service method is called with the right arguments
5. **Exception mapping**: service exceptions caught by the action produce the intended result type (exceptions handled by exception-handling middleware are an integration concern)
