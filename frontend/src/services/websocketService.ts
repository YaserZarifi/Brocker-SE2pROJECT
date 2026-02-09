/**
 * WebSocket Service for BourseChain
 * Sprint 5 - Real-time notifications + stock price updates
 *
 * Manages WebSocket connections to:
 *   /ws/notifications/?token=<jwt>  - User-specific notifications (auth required)
 *   /ws/stocks/                     - Live stock price updates (public)
 *
 * Features:
 *   - Auto-reconnect with exponential backoff
 *   - JWT authentication for notification channel
 *   - Event-based message handling via callbacks
 */

import { getAccessToken } from "./api";

type MessageHandler = (data: any) => void;

interface WebSocketConfig {
  url: string;
  onMessage: MessageHandler;
  onOpen?: () => void;
  onClose?: () => void;
  requiresAuth?: boolean;
}

class WebSocketConnection {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private baseDelay = 1000; // 1 second
  private maxDelay = 30000; // 30 seconds
  private intentionallyClosed = false;

  constructor(config: WebSocketConfig) {
    this.config = config;
  }

  connect(): void {
    this.intentionallyClosed = false;
    this.reconnectAttempts = 0;
    this._connect();
  }

  private _connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    let url = this.config.url;

    // Add JWT token for authenticated connections
    if (this.config.requiresAuth) {
      const token = getAccessToken();
      if (!token) {
        console.warn("[WS] No auth token available, skipping connection to", url);
        return;
      }
      const separator = url.includes("?") ? "&" : "?";
      url = `${url}${separator}token=${token}`;
    }

    // Build full WebSocket URL
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const fullUrl = `${protocol}//${host}${url}`;

    try {
      this.ws = new WebSocket(fullUrl);

      this.ws.onopen = () => {
        console.log("[WS] Connected:", this.config.url);
        this.reconnectAttempts = 0;
        this.config.onOpen?.();
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.config.onMessage(message);
        } catch (e) {
          console.error("[WS] Failed to parse message:", e);
        }
      };

      this.ws.onclose = (event) => {
        console.log("[WS] Disconnected:", this.config.url, "code:", event.code);
        this.config.onClose?.();

        if (!this.intentionallyClosed) {
          this._scheduleReconnect();
        }
      };

      this.ws.onerror = (error) => {
        console.error("[WS] Error on", this.config.url, error);
      };
    } catch (e) {
      console.error("[WS] Failed to create WebSocket:", e);
      this._scheduleReconnect();
    }
  }

  private _scheduleReconnect(): void {
    if (this.intentionallyClosed) return;
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.warn("[WS] Max reconnect attempts reached for", this.config.url);
      return;
    }

    const delay = Math.min(
      this.baseDelay * Math.pow(2, this.reconnectAttempts),
      this.maxDelay
    );
    this.reconnectAttempts++;

    console.log(
      `[WS] Reconnecting to ${this.config.url} in ${delay}ms (attempt ${this.reconnectAttempts})`
    );

    this.reconnectTimer = setTimeout(() => {
      this._connect();
    }, delay);
  }

  disconnect(): void {
    this.intentionallyClosed = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// ============================================
// Singleton WebSocket Manager
// ============================================

class WebSocketManager {
  private notificationWs: WebSocketConnection | null = null;
  private stockWs: WebSocketConnection | null = null;
  private notificationHandlers: MessageHandler[] = [];
  private stockHandlers: MessageHandler[] = [];

  /**
   * Connect to the notification WebSocket (requires auth).
   * Call this after successful login.
   */
  connectNotifications(): void {
    if (this.notificationWs?.isConnected()) return;

    this.notificationWs?.disconnect();
    this.notificationWs = new WebSocketConnection({
      url: "/ws/notifications/",
      requiresAuth: true,
      onMessage: (message) => {
        this.notificationHandlers.forEach((handler) => handler(message));
      },
      onOpen: () => {
        console.log("[WS] Notification channel ready");
      },
    });
    this.notificationWs.connect();
  }

  /**
   * Connect to the stock price WebSocket (public).
   * Can be called anytime.
   */
  connectStockPrices(): void {
    if (this.stockWs?.isConnected()) return;

    this.stockWs?.disconnect();
    this.stockWs = new WebSocketConnection({
      url: "/ws/stocks/",
      requiresAuth: false,
      onMessage: (message) => {
        this.stockHandlers.forEach((handler) => handler(message));
      },
      onOpen: () => {
        console.log("[WS] Stock prices channel ready");
      },
    });
    this.stockWs.connect();
  }

  /** Disconnect notification WebSocket (call on logout). */
  disconnectNotifications(): void {
    this.notificationWs?.disconnect();
    this.notificationWs = null;
  }

  /** Disconnect stock price WebSocket. */
  disconnectStockPrices(): void {
    this.stockWs?.disconnect();
    this.stockWs = null;
  }

  /** Disconnect all WebSocket connections. */
  disconnectAll(): void {
    this.disconnectNotifications();
    this.disconnectStockPrices();
  }

  /** Register a handler for notification messages. */
  onNotification(handler: MessageHandler): () => void {
    this.notificationHandlers.push(handler);
    return () => {
      this.notificationHandlers = this.notificationHandlers.filter(
        (h) => h !== handler
      );
    };
  }

  /** Register a handler for stock price update messages. */
  onStockUpdate(handler: MessageHandler): () => void {
    this.stockHandlers.push(handler);
    return () => {
      this.stockHandlers = this.stockHandlers.filter((h) => h !== handler);
    };
  }
}

// Export singleton instance
export const wsManager = new WebSocketManager();
