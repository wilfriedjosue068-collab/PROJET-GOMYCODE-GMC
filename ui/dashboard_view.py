"""Tableau de bord (UC8) : indicateurs du mois, graphiques, alertes (UC7)."""
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from services import budget_service, report_service, transaction_service
from ui import theme
from ui.widgets import Card, MonthSelector, StatCard, page_header
from utils.dates import month_label
from utils.formatters import format_amount, format_date, format_percent


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user, app=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.app = app

        right = page_header(self, "Tableau de bord", "Vue d'ensemble de vos finances")
        self.month_selector = MonthSelector(right, on_change=lambda m: self.refresh())
        self.month_selector.pack()

        # --- Indicateurs ---
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=28)
        self.card_income = StatCard(stats, "Revenus du mois", theme.INCOME)
        self.card_expense = StatCard(stats, "Dépenses du mois", theme.EXPENSE)
        self.card_balance = StatCard(stats, "Solde du mois")
        self.card_global = StatCard(stats, "Solde global", theme.PRIMARY)
        for i, card in enumerate((self.card_income, self.card_expense,
                                  self.card_balance, self.card_global)):
            stats.grid_columnconfigure(i, weight=1, uniform="stats")
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 12, 0))

        # --- Alertes + dernières transactions (réservé en bas en premier) ---
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=28, pady=(0, 24))

        # --- Graphiques ---
        charts = ctk.CTkFrame(self, fg_color="transparent")
        charts.pack(fill="both", expand=True, padx=28, pady=14)
        charts.grid_columnconfigure(0, weight=2, uniform="charts")
        charts.grid_columnconfigure(1, weight=3, uniform="charts")
        charts.grid_rowconfigure(0, weight=1)

        self.pie_card = Card(charts)
        self.pie_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ctk.CTkLabel(self.pie_card, text="Dépenses par catégorie", font=theme.SUBTITLE,
                     anchor="w").pack(fill="x", padx=16, pady=(12, 0))
        self.pie_fig = Figure(figsize=(4, 2.4), dpi=100)
        self.pie_canvas = FigureCanvasTkAgg(self.pie_fig, master=self.pie_card)
        self.pie_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        self.bar_card = Card(charts)
        self.bar_card.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(self.bar_card, text="Évolution sur 6 mois", font=theme.SUBTITLE,
                     anchor="w").pack(fill="x", padx=16, pady=(12, 0))
        self.bar_fig = Figure(figsize=(6, 2.4), dpi=100)
        self.bar_canvas = FigureCanvasTkAgg(self.bar_fig, master=self.bar_card)
        self.bar_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        bottom.grid_columnconfigure(0, weight=2, uniform="bottom")
        bottom.grid_columnconfigure(1, weight=3, uniform="bottom")

        alerts_card = Card(bottom, height=205)
        alerts_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        alerts_card.pack_propagate(False)
        ctk.CTkLabel(alerts_card, text="Alertes budget", font=theme.SUBTITLE,
                     anchor="w").pack(fill="x", padx=16, pady=(12, 4))
        self.alerts_box = ctk.CTkFrame(alerts_card, fg_color="transparent")
        self.alerts_box.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        recent_card = Card(bottom, height=205)
        recent_card.grid(row=0, column=1, sticky="nsew")
        recent_card.pack_propagate(False)
        ctk.CTkLabel(recent_card, text="Dernières transactions", font=theme.SUBTITLE,
                     anchor="w").pack(fill="x", padx=16, pady=(12, 4))
        self.recent_box = ctk.CTkFrame(recent_card, fg_color="transparent")
        self.recent_box.pack(fill="both", expand=True, padx=16, pady=(0, 10))

    # ------------------------------------------------------------------
    def refresh(self):
        month = self.month_selector.get()
        uid = self.user["id"]
        summary = report_service.get_monthly_summary(uid, month)
        self.card_income.set(format_amount(summary["revenus"]))
        self.card_expense.set(format_amount(summary["depenses"]))
        self.card_balance.set(format_amount(summary["solde"], signed=True),
                              theme.INCOME if summary["solde"] >= 0 else theme.EXPENSE)
        balance = report_service.get_global_balance(uid)
        self.card_global.set(format_amount(balance),
                             theme.PRIMARY if balance >= 0 else theme.EXPENSE)

        self._draw_pie(report_service.get_expenses_by_category(uid, month), month)
        self._draw_bars(report_service.get_monthly_trend(uid, month, 6))
        self._fill_alerts(budget_service.check_overruns(uid, month))
        self._fill_recent(transaction_service.list_transactions(uid, limit=5))

    def on_theme_changed(self):
        if self.winfo_ismapped():
            self.refresh()

    # ------------------------------------------------------------------
    def _style_axes(self, fig, ax):
        bg, fg = theme.pick(theme.CARD), theme.pick(theme.TEXT)
        fig.set_facecolor(bg)
        ax.set_facecolor(bg)
        ax.tick_params(colors=fg, labelsize=8)
        for spine in ax.spines.values():
            spine.set_visible(False)
        return fg

    def _draw_pie(self, data, month):
        self.pie_fig.clear()
        ax = self.pie_fig.add_subplot(111)
        fg = self._style_axes(self.pie_fig, ax)
        if not data:
            ax.text(0.5, 0.5, f"Aucune dépense\nen {month_label(month).lower()}",
                    ha="center", va="center", color=fg, fontsize=10)
            ax.axis("off")
        else:
            if len(data) > 6:  # au-delà de 6 catégories, on regroupe le reste
                data = data[:5] + [("Autres", sum(v for _, v in data[5:]))]
            labels, values = zip(*data)
            wedges, _ = ax.pie(values, colors=theme.CHART_PALETTE[:len(values)],
                               startangle=90, counterclock=False,
                               wedgeprops={"width": 0.38, "edgecolor": theme.pick(theme.CARD)})
            total = sum(values)
            ax.text(0, 0, format_amount(total, with_currency=False), ha="center",
                    va="center", color=fg, fontsize=10, fontweight="bold")
            short = [l if len(l) <= 14 else l[:13] + "…" for l in labels]
            ax.legend(wedges, [f"{l} ({v / total:.0%})" for l, v in zip(short, values)],
                      loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False,
                      fontsize=8, labelcolor=fg)
            ax.set_aspect("equal")
        self.pie_fig.subplots_adjust(left=0.0, right=0.55, top=0.95, bottom=0.05)
        self.pie_canvas.draw_idle()

    def _draw_bars(self, trend):
        self.bar_fig.clear()
        ax = self.bar_fig.add_subplot(111)
        fg = self._style_axes(self.bar_fig, ax)
        x = range(len(trend))
        width = 0.38
        ax.bar([i - width / 2 for i in x], [t["revenus"] for t in trend], width,
               label="Revenus", color=theme.INCOME)
        ax.bar([i + width / 2 for i in x], [t["depenses"] for t in trend], width,
               label="Dépenses", color=theme.EXPENSE)
        ax.set_xticks(list(x))
        ax.set_xticklabels([month_label(t["month"], short=True) for t in trend])
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1000:,.0f} k".replace(",", " ")))
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
        peak = max([t["revenus"] for t in trend] + [t["depenses"] for t in trend] + [1])
        ax.set_ylim(0, peak * 1.25)  # marge pour la légende
        ax.legend(frameon=False, fontsize=8, labelcolor=fg, loc="upper left", ncol=2)
        self.bar_fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.12)
        self.bar_canvas.draw_idle()

    def _fill_alerts(self, alerts):
        for w in self.alerts_box.winfo_children():
            w.destroy()
        if not alerts:
            ctk.CTkLabel(self.alerts_box, text="✓ Tous vos budgets sont respectés.",
                         text_color=theme.INCOME, font=theme.BODY, anchor="w").pack(fill="x")
            return
        for a in alerts[:4]:
            if a["level"] == "danger":
                text = (f"⚠ {a['category']} : budget dépassé de "
                        f"{format_amount(-a['remaining'])} ({format_percent(a['ratio'])})")
            else:
                text = f"● {a['category']} : {format_percent(a['ratio'])} du budget consommé"
            ctk.CTkLabel(self.alerts_box, text=text, anchor="w", font=theme.BODY,
                         text_color=theme.LEVEL_COLORS[a["level"]]).pack(fill="x", pady=2)

    def _fill_recent(self, transactions):
        for w in self.recent_box.winfo_children():
            w.destroy()
        if not transactions:
            ctk.CTkLabel(self.recent_box, text="Aucune transaction pour le moment.",
                         text_color=theme.MUTED, anchor="w").pack(fill="x")
            return
        for t in transactions:
            row = ctk.CTkFrame(self.recent_box, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=format_date(t["date"]), width=90, anchor="w",
                         text_color=theme.MUTED, font=theme.BODY).pack(side="left")
            label = t["category"] + (f" - {t['description']}" if t["description"] else "")
            ctk.CTkLabel(row, text=label, anchor="w", font=theme.BODY).pack(side="left")
            sign = 1 if t["type"] == "revenu" else -1
            ctk.CTkLabel(row, text=format_amount(sign * t["amount"], signed=True),
                         font=theme.BODY_BOLD, anchor="e",
                         text_color=theme.INCOME if sign > 0 else theme.EXPENSE
                         ).pack(side="right")
