import { createBrowserRouter, Navigate } from "react-router-dom";
import { MainLayout } from "@/components/layout/MainLayout";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import DashboardPage from "@/pages/DashboardPage";
import MarketPage from "@/pages/MarketPage";
import StockDetailPage from "@/pages/StockDetailPage";
import PortfolioPage from "@/pages/PortfolioPage";
import OrdersPage from "@/pages/OrdersPage";
import TransactionsPage from "@/pages/TransactionsPage";
import NotificationsPage from "@/pages/NotificationsPage";
import AdminPage from "@/pages/AdminPage";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/register",
    element: <RegisterPage />,
  },
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: "dashboard", element: <DashboardPage /> },
      { path: "market", element: <MarketPage /> },
      { path: "market/:symbol", element: <StockDetailPage /> },
      { path: "portfolio", element: <PortfolioPage /> },
      { path: "orders", element: <OrdersPage /> },
      { path: "transactions", element: <TransactionsPage /> },
      { path: "notifications", element: <NotificationsPage /> },
      { path: "admin", element: <AdminPage /> },
    ],
  },
]);
