import { CreatePurchaseResponse, PurchaseDTO } from "../../models/purchases/PurchaseDTO";

export interface IPurchasesAPI {
  createPurchase(data: { user_id: number; flight_id: number; user_email?: string }): Promise<CreatePurchaseResponse>;
  getUserPurchases(userId: number): Promise<PurchaseDTO[]>;
  cancelPurchase(purchaseId: number, token?: string | null): Promise<PurchaseDTO>;
}
