# Expected Test Cases — OrderService (golden list)

Hand-derived from the branches in `src/order-service.ts`, following the
INCLUDE/EXCLUDE criteria in `test-case-generation-strategy.md`. A correct
`generate-tests` run against this fixture must produce test cases equivalent
to the list below (naming may vary in wording, but each covered branch and
observable outcome must be present, and no EXCLUDE-rule violations added).

Notes for scoring:
- Cases 3 and 4 together cover BOTH branches of the private `#applyDiscount`
  helper, reachable only through `createOrder` inputs (CRITICAL private-method
  rule). Case 4 uses total exactly 100 to pin the `>=` boundary.
- Quantity 0 and negative quantity hit the same `quantity <= 0` branch — one
  case only (EXCLUDE: duplicate scenarios with same observable result).
- Cases 11–13 exercise the `setTimeout`-based delay in `retryPayment` and
  require fake timers.
- Logging assertions are part of the Then clauses wherever the code logs;
  they are not separate cases (same code path).

## Test Cases for OrderService.createOrder

### 1. createOrder_emptyProductId_throwsValidationError
- **Given:** OrderRequest with productId `""` (or whitespace-only), quantity 1, valid customerId
- **When:** createOrder is called
- **Then:** ValidationError is thrown; repository.save is never called
- **Code branch:** Validation — `request.productId.trim() === ''`

### 2. createOrder_quantityZero_throwsValidationError
- **Given:** OrderRequest with valid productId and quantity 0
- **When:** createOrder is called
- **Then:** ValidationError is thrown; repository.save is never called
- **Code branch:** Validation — `request.quantity <= 0`

### 3. createOrder_validRequestBelowDiscountThreshold_savesAndReturnsOrder
- **Given:** Valid OrderRequest with unitPrice and quantity giving total < 100 (e.g. unitPrice 20, quantity 2); repository.save resolves with the passed order
- **When:** createOrder is called
- **Then:** Returned Order maps productId, customerId, quantity from the request; total is 40 (no discount); repository.save was called with that order; logger.info was called with `Order created: {id}` for the saved order's id
- **Code branch:** Happy path + `#applyDiscount` no-discount branch (total < 100)

### 4. createOrder_totalAtDiscountThreshold_appliesTenPercentDiscount
- **Given:** Valid OrderRequest with unitPrice and quantity giving total exactly 100 (e.g. unitPrice 50, quantity 2); repository.save resolves with the passed order
- **When:** createOrder is called
- **Then:** Order saved and returned with total 90 (10% discount applied)
- **Code branch:** `#applyDiscount` discount branch (total >= 100), reached only via createOrder inputs

## Test Cases for OrderService.processPayment

### 5. processPayment_chargeSucceeds_returnsReceiptId
- **Given:** Order with id "order-1" and total 50; gateway.charge resolves true
- **When:** processPayment is called
- **Then:** Returns `receipt-order-1`; gateway.charge was called with ("order-1", 50); logger.error was never called
- **Code branch:** Success path — `charged === true`

### 6. processPayment_chargeDeclined_throwsPaymentFailedError
- **Given:** Order; gateway.charge resolves false
- **When:** processPayment is called
- **Then:** PaymentFailedError is thrown; logger.error was called with `Payment declined for order {id}`
- **Code branch:** Declined path — `!charged`

### 7. processPayment_gatewayRejects_wrapsErrorInPaymentFailedError
- **Given:** Order; gateway.charge rejects with an underlying error
- **When:** processPayment is called
- **Then:** PaymentFailedError is thrown wrapping the underlying error as `cause`; logger.error was called with `Payment gateway error for order {id}`
- **Code branch:** External-failure path — catch around `gateway.charge`

## Test Cases for OrderService.getOrder

### 8. getOrder_orderExists_returnsOrder
- **Given:** repository.findById resolves with an existing Order for id "order-1"
- **When:** getOrder("order-1") is called
- **Then:** The found Order is returned; repository.findById was called with "order-1"
- **Code branch:** Found path

### 9. getOrder_orderNotFound_throwsOrderNotFoundError
- **Given:** repository.findById resolves null
- **When:** getOrder is called
- **Then:** OrderNotFoundError is thrown (message contains the requested id)
- **Code branch:** Not-found path — `order === null`

## Test Cases for OrderService.retryPayment

### 10. retryPayment_maxAttemptsLessThanOne_throwsValidationError
- **Given:** Any Order and maxAttempts 0
- **When:** retryPayment is called
- **Then:** ValidationError is thrown; gateway.charge is never called
- **Code branch:** Validation — `maxAttempts < 1`

### 11. retryPayment_firstAttemptSucceeds_returnsReceiptWithoutDelay
- **Given:** gateway.charge resolves true on the first call; maxAttempts 3
- **When:** retryPayment is called
- **Then:** Returns the receipt id; gateway.charge was called exactly once; no delay timer was scheduled
- **Code branch:** Retry loop — success on attempt 1, delay branch not taken

### 12. retryPayment_secondAttemptSucceeds_waitsOneSecondBetweenAttempts
- **Given:** Fake timers enabled; gateway.charge resolves false on attempt 1 and true on attempt 2; maxAttempts 3
- **When:** retryPayment is called and timers are advanced by 1000 ms after the first failure
- **Then:** Returns the receipt id; gateway.charge was called exactly twice; the second attempt happens only after the 1000 ms delay elapses
- **Code branch:** Retry loop — failure then success; `attempt < maxAttempts` delay branch taken

### 13. retryPayment_allAttemptsFail_throwsLastPaymentFailedError
- **Given:** Fake timers enabled; gateway.charge always resolves false; maxAttempts 2
- **When:** retryPayment is called and timers are advanced past the inter-attempt delay
- **Then:** PaymentFailedError (the last attempt's error) is thrown; gateway.charge was called exactly twice; no delay is scheduled after the final attempt
- **Code branch:** Retry loop exhausted — `throw lastError`
