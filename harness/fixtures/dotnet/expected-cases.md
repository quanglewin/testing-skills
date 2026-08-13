# Expected Test Cases — .NET Fixture (OrderFixture)

Golden list of test cases a correct `/generate-tests` run must produce for this fixture.
Hand-derived from the code branches, one case per distinct branch/observable outcome
(per `test-case-generation-strategy.md` INCLUDE/EXCLUDE rules). C# naming:
`Method_State_Outcome` in PascalCase.

Note: both branches of the private helper `CalculateDiscount` must be covered
indirectly through `CreateOrder` inputs (cases 3 and 4) — never by testing the
private method directly.

## Test Cases for OrderService.CreateOrder

### 1. CreateOrder_EmptyProductId_ThrowsArgumentException
- **Given:** OrderRequest with an empty (or whitespace) ProductId
- **When:** CreateOrder is called
- **Then:** ArgumentException is thrown; nothing is saved to the repository
- **Code branch:** Validation — `string.IsNullOrWhiteSpace(request.ProductId)` guard

### 2. CreateOrder_ZeroOrNegativeQuantity_ThrowsArgumentException
- **Given:** OrderRequest with valid ProductId and Quantity of 0
- **When:** CreateOrder is called
- **Then:** ArgumentException is thrown; nothing is saved to the repository
- **Code branch:** Validation — `request.Quantity <= 0` guard

### 3. CreateOrder_TotalBelowDiscountThreshold_SavesOrderWithFullTotal
- **Given:** Valid OrderRequest whose UnitPrice * Quantity is below 100 (e.g. 40m * 2 = 80m); repository Save returns the saved order
- **When:** CreateOrder is called
- **Then:** The order passed to Save maps all request fields (ProductId, Quantity, CustomerId) and has Total equal to the undiscounted subtotal (80m); the repository's return value is returned
- **Code branch:** Happy path + private CalculateDiscount `total < 100` branch (no discount)

### 4. CreateOrder_TotalAtOrAboveDiscountThreshold_SavesOrderWithDiscountedTotal
- **Given:** Valid OrderRequest whose UnitPrice * Quantity is at least 100 (e.g. 50m * 4 = 200m)
- **When:** CreateOrder is called
- **Then:** The saved order's Total is the subtotal minus 10% (180m)
- **Code branch:** Private CalculateDiscount `total >= 100` branch (10% discount), reached via public API

## Test Cases for OrderService.ProcessPayment

### 5. ProcessPayment_GatewayApproves_ReturnsReceiptId
- **Given:** An Order; payment gateway Charge returns true for the order's CustomerId and Total
- **When:** ProcessPayment is called
- **Then:** A receipt id of the form `receipt-{order.Id}` is returned
- **Code branch:** Success path — gateway approved

### 6. ProcessPayment_GatewayDeclines_ThrowsPaymentFailedException
- **Given:** An Order; payment gateway Charge returns false
- **When:** ProcessPayment is called
- **Then:** PaymentFailedException is thrown
- **Code branch:** `!approved` branch — declined payment

### 7. ProcessPayment_GatewayTimesOut_ThrowsPaymentFailedExceptionWrappingTimeout
- **Given:** An Order; payment gateway Charge throws TimeoutException
- **When:** ProcessPayment is called
- **Then:** PaymentFailedException is thrown with the TimeoutException as InnerException
- **Code branch:** External-failure path — `catch (TimeoutException)` wrap

## Test Cases for OrderService.GetOrder

### 8. GetOrder_ExistingId_ReturnsOrder
- **Given:** Repository FindById returns an order for the given id
- **When:** GetOrder is called
- **Then:** That order is returned
- **Code branch:** Found path

### 9. GetOrder_UnknownId_ThrowsOrderNotFoundException
- **Given:** Repository FindById returns null
- **When:** GetOrder is called
- **Then:** OrderNotFoundException is thrown (carrying the requested id)
- **Code branch:** Not-found path — `?? throw new OrderNotFoundException(id)`

## Test Cases for OrdersController.GetOrder

### 10. GetOrder_ExistingId_Returns200WithOrder
- **Given:** IOrderService.GetOrder returns an order
- **When:** GET /orders/{id} action is invoked
- **Then:** OkObjectResult (200) containing the order is returned
- **Code branch:** Success path — `Ok(...)`

### 11. GetOrder_UnknownId_Returns404
- **Given:** IOrderService.GetOrder throws OrderNotFoundException
- **When:** GET /orders/{id} action is invoked
- **Then:** NotFoundResult (404) is returned
- **Code branch:** `catch (OrderNotFoundException)` → `NotFound()`

## Test Cases for OrdersController.CreateOrder

### 12. CreateOrder_ValidRequest_Returns201WithCreatedOrder
- **Given:** IOrderService.CreateOrder returns a created order
- **When:** POST /orders action is invoked
- **Then:** CreatedAtActionResult (201) is returned, pointing at GetOrder with the new order's id and containing the order
- **Code branch:** Success path — `CreatedAtAction(...)`

### 13. CreateOrder_InvalidRequest_Returns400
- **Given:** IOrderService.CreateOrder throws ArgumentException
- **When:** POST /orders action is invoked
- **Then:** BadRequestObjectResult (400) is returned with the exception message
- **Code branch:** `catch (ArgumentException)` → `BadRequest(...)`
