export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class OrderNotFoundError extends Error {
  constructor(orderId: string) {
    super(`Order not found: ${orderId}`);
    this.name = 'OrderNotFoundError';
  }
}

export class PaymentFailedError extends Error {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = 'PaymentFailedError';
  }
}
