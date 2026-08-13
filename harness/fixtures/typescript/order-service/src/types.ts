export interface Product {
  id: string;
  name: string;
  price: number;
}

export interface OrderRequest {
  productId: string;
  quantity: number;
  customerId: string;
  unitPrice: number;
}

export interface Order {
  id: string;
  productId: string;
  customerId: string;
  quantity: number;
  total: number;
}
