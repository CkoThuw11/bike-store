// ============================================================
// FILE: src/app/shared/types/index.ts
// ============================================================

// ----------------------------------------------------------
// Auth
// ----------------------------------------------------------
export type Role = 'ADMIN' | 'CUSTOMER';

export interface UserDto {
  user_id: number;
  email: string;
  username: string;
  fullname: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenPairDto {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export interface LoginResponse {
  user: UserDto;
  token_pair: TokenPairDto;
}

export interface RegisterResponse {
  user: UserDto;
}

export interface RefreshResponse {
  token_pair: TokenPairDto;
}

// Commands
export interface LoginCommand {
  email: string;
  password: string;
}

export interface RegisterCommand {
  email: string;
  password: string;
  username: string;
  fullname: string;
}

// ----------------------------------------------------------
// API Error
// ----------------------------------------------------------
export interface ApiError {
  status: number;
  error: string;
  message: string;
  meta?: unknown[];
}

export interface AppError {
  status: number;
  code: string;
  message: string;
  fieldErrors: Record<string, string>;
  raw: unknown;
}

// ----------------------------------------------------------
// Brand
// ----------------------------------------------------------
export interface BrandDto {
  brand_id: number;
  brand_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateBrandCommand {
  brand_name: string;
}

export interface UpdateBrandCommand {
  brand_name: string;
}

// ----------------------------------------------------------
// Category
// ----------------------------------------------------------
export interface CategoryDto {
  category_id: number;
  category_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateCategoryCommand {
  category_name: string;
}

export interface UpdateCategoryCommand {
  category_name: string;
}

// ----------------------------------------------------------
// Product
// ----------------------------------------------------------
export interface ProductDto {
  product_id: number;
  product_name: string;
  brand_id: number;
  category_id: number;
  model_year: number;
  list_price: string | number;
  is_active: boolean;
}

export interface CreateProductCommand {
  product_name: string;
  brand_id: number;
  category_id: number;
  model_year: number;
  list_price: string;
}

export interface UpdateProductCommand {
  product_name?: string;
  brand_id?: number;
  category_id?: number;
  model_year?: number;
  list_price?: string;
}

// ----------------------------------------------------------
// Store
// ----------------------------------------------------------
export interface StoreDto {
  store_id: number;
  store_name: string;
  phone: string;
  email: string;
  street: string;
  city: string;
  state: string;
  zip_code: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateStoreCommand {
  store_name: string;
  phone: string;
  email: string;
  street: string;
  city: string;
  state: string;
  zip_code: string;
}

export interface UpdateStoreCommand {
  store_name?: string;
  phone?: string;
  email?: string;
  street?: string;
  city?: string;
  state?: string;
  zip_code?: string;
}

// ----------------------------------------------------------
// Staff
// ----------------------------------------------------------
export interface StaffDto {
  staff_id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  store_id: number;
  manager_id: number | null;
  is_active: boolean;
}

export interface CreateStaffCommand {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  store_id: number;
  manager_id: number | null;
}

export interface UpdateStaffCommand {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  store_id?: number;
  manager_id?: number | null;
}

// ----------------------------------------------------------
// Stock
// ----------------------------------------------------------
export interface StockDto {
  store_id: number;
  product_id: number;
  quantity: number;
  created_at: string;
  updated_at: string;
}

export interface UpdateStockCommand {
  quantity: number;
}

// ----------------------------------------------------------
// Customer
// ----------------------------------------------------------
export interface CustomerDto {
  customer_id: number;
  first_name: string;
  last_name: string;
  phone: string;
  email: string;
  street: string;
  city: string;
  state: string;
  zip_code: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CustomerAddress {
  street: string;
  city: string;
  state: string;
  zip_code: string;
}

export interface CreateCustomerCommand {
  first_name: string;
  last_name: string;
  phone: string;
  email: string;
  address: CustomerAddress;
}

export interface UpdateCustomerCommand {
  first_name?: string;
  last_name?: string;
  phone?: string;
  email?: string;
  address?: CustomerAddress;
}

// ----------------------------------------------------------
// Order
// ----------------------------------------------------------
export type OrderStatus = 1 | 2 | 3 | 4 | 5;

export const ORDER_STATUS_LABELS: Record<OrderStatus, string> = {
  1: 'PENDING',
  2: 'PROCESSING',
  3: 'SHIPPED',
  4: 'COMPLETED',
  5: 'CANCELLED',
};

export interface OrderDto {
  order_id: number;
  customer_id: number;
  order_status: OrderStatus;
  order_date: string;
  required_date: string | null;
  shipped_date: string | null;
  store_id: number;
  staff_id: number;
  created_at: string;
  updated_at: string;
}

export interface CreateOrderCommand {
  customer_id: number;
}

export interface CheckoutOrderCommand {
  required_date: string;
}

export interface UpdateOrderCommand {
  order_status?: OrderStatus;
  required_date?: string;
  shipped_date?: string;
}

// ----------------------------------------------------------
// Order Item
// ----------------------------------------------------------
export interface OrderItemDto {
  order_id: number;
  item_id: number;
  product_id: number;
  quantity: number;
  list_price: string | number;
  discount: string | number;
  created_at: string;
  updated_at: string;
}

export interface CreateOrderItemCommand {
  order_id: number;
  product_id: number;
  quantity: number;
  discount: string;
}

export interface UpdateOrderItemCommand {
  quantity?: number;
}