import { OrderNotFoundError, PaymentFailedError, ValidationError } from './errors';
import type { Logger } from './logger';
import type { OrderRepository } from './order-repository';
import type { PaymentGateway } from './payment-gateway';
import type { Order, OrderRequest } from './types';

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

export class OrderService {
  readonly #repository: OrderRepository;
  readonly #gateway: PaymentGateway;
  readonly #logger: Logger;

  constructor(repository: OrderRepository, gateway: PaymentGateway, logger: Logger) {
    this.#repository = repository;
    this.#gateway = gateway;
    this.#logger = logger;
  }

  async createOrder(request: OrderRequest): Promise<Order> {
    if (request.productId.trim() === '') {
      throw new ValidationError('productId must not be empty');
    }
    if (request.quantity <= 0) {
      throw new ValidationError('quantity must be greater than zero');
    }

    const order: Order = {
      id: `order-${Date.now()}-${Math.floor(Math.random() * 1_000_000)}`,
      productId: request.productId,
      customerId: request.customerId,
      quantity: request.quantity,
      total: this.#applyDiscount(request.unitPrice * request.quantity),
    };

    const saved = await this.#repository.save(order);
    this.#logger.info(`Order created: ${saved.id}`);
    return saved;
  }

  async processPayment(order: Order): Promise<string> {
    let charged: boolean;
    try {
      charged = await this.#gateway.charge(order.id, order.total);
    } catch (error) {
      this.#logger.error(`Payment gateway error for order ${order.id}`);
      throw new PaymentFailedError(`Payment failed for order ${order.id}`, { cause: error });
    }

    if (!charged) {
      this.#logger.error(`Payment declined for order ${order.id}`);
      throw new PaymentFailedError(`Payment declined for order ${order.id}`);
    }

    return `receipt-${order.id}`;
  }

  async getOrder(id: string): Promise<Order> {
    const order = await this.#repository.findById(id);
    if (order === null) {
      throw new OrderNotFoundError(id);
    }
    return order;
  }

  async retryPayment(order: Order, maxAttempts: number): Promise<string> {
    if (maxAttempts < 1) {
      throw new ValidationError('maxAttempts must be at least 1');
    }

    let lastError: unknown;
    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      try {
        return await this.processPayment(order);
      } catch (error) {
        lastError = error;
        if (attempt < maxAttempts) {
          await delay(1000);
        }
      }
    }
    throw lastError;
  }

  #applyDiscount(total: number): number {
    if (total >= 100) {
      return total * 0.9;
    }
    return total;
  }
}
