import { create } from "zustand";
import type { Notification } from "@/types";
import { notificationService } from "@/services/notificationService";
import { wsManager } from "@/services/websocketService";

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  wsConnected: boolean;
  fetchNotifications: () => Promise<void>;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  addNotification: (notification: Notification) => void;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  isLoading: false,
  wsConnected: false,

  fetchNotifications: async () => {
    set({ isLoading: true });
    try {
      const notifications = await notificationService.getNotifications();
      const unreadCount = notifications.filter((n) => !n.read).length;
      set({ notifications, unreadCount, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  markAsRead: (id) => {
    // Optimistic UI update
    set((state) => {
      const notifications = state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      );
      return {
        notifications,
        unreadCount: notifications.filter((n) => !n.read).length,
      };
    });
    // Fire API call in background
    notificationService.markAsRead(id).catch(() => {});
  },

  markAllAsRead: () => {
    // Optimistic UI update
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
      unreadCount: 0,
    }));
    // Fire API call in background
    notificationService.markAllAsRead().catch(() => {});
  },

  addNotification: (notification) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: get().unreadCount + (notification.read ? 0 : 1),
    }));
  },

  connectWebSocket: () => {
    if (get().wsConnected) return;

    // Register handler for incoming WebSocket notifications
    wsManager.onNotification((message) => {
      if (message.type === "notification" && message.data) {
        get().addNotification(message.data as Notification);
      }
    });

    // Connect to notification WebSocket
    wsManager.connectNotifications();
    set({ wsConnected: true });
  },

  disconnectWebSocket: () => {
    wsManager.disconnectNotifications();
    set({ wsConnected: false });
  },
}));
