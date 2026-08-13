import type { Order } from './types';

export interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<Order>;
  findAll(): Promise<Order[]>;
}
