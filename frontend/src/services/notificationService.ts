import api from "./api";
import type { Notification } from "@/types";

// ============================================
// Notification Service - Notification APIs
// ============================================

export const notificationService = {
  async getNotifications(): Promise<Notification[]> {
    const { data } = await api.get<{ results: Notification[] }>("/notifications/");
    const notifs = Array.isArray(data) ? data : data.results;
    return notifs;
  },

  async markAsRead(id: string): Promise<void> {
    await api.patch(`/notifications/${id}/`, { read: true });
  },

  async markAllAsRead(): Promise<void> {
    await api.post("/notifications/mark-all-read/");
  },

  async getUnreadCount(): Promise<number> {
    const { data } = await api.get<{ unreadCount: number }>("/notifications/unread-count/");
    return data.unreadCount;
  },
};
