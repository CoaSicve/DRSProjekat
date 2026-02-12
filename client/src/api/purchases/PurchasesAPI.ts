import axios, { AxiosInstance } from "axios";
import { CreatePurchaseResponse, PurchaseDTO } from "../../models/purchases/PurchaseDTO";
import { IPurchasesAPI } from "./IPurchasesAPI";

export class PurchasesAPI implements IPurchasesAPI {
  private readonly axiosInstance: AxiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: import.meta.env.VITE_GATEWAY_URL,
      headers: { "Content-Type": "application/json" },
    });
  }

  async createPurchase(data: { user_id: number; flight_id: number; user_email?: string }): Promise<CreatePurchaseResponse> {
    return (await this.axiosInstance.post<CreatePurchaseResponse>("/purchase", data)).data;
  }

  async getUserPurchases(userId: number): Promise<PurchaseDTO[]> {
    return (await this.axiosInstance.get<PurchaseDTO[]>(`/purchases/${userId}`)).data;
  }

  async cancelPurchase(purchaseId: number, token?: string | null): Promise<PurchaseDTO> {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : undefined;
    return (await this.axiosInstance.put<PurchaseDTO>(`/purchases/${purchaseId}/cancel`, null, config)).data;
  }
}
