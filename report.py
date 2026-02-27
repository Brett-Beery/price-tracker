import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference
from database import get_all_latest_prices, get_price_drops, init_db
import datetime
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Styles ---
BG_HEADER = "2F4F8F"
BG_SECTION = "D9E1F2"
BG_ALERT = "FFE0E0"
BG_GOOD = "E0FFE0"
WHITE = "FFFFFF"

def make_border():
    thin = Side(style="thin")
    return Border(left=thin, right=thin, top=thin, bottom=thin)

def make_header_cell(ws, row, col, value, width=None):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(name="Calibri", bold=True, size=11, color=WHITE)
    cell.fill = PatternFill("solid", fgColor=BG_HEADER)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = make_border()
    return cell

def make_section_cell(ws, row, col, value):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(name="Calibri", bold=True, size=11)
    cell.fill = PatternFill("solid", fgColor=BG_SECTION)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = make_border()
    return cell


def build_report():
    init_db()
    today = datetime.date.today().strftime("%Y-%m-%d")
    wb = openpyxl.Workbook()

    # =====================
    # SHEET 1 - PRICE SNAPSHOT
    # =====================
    ws1 = wb.active
    ws1.title = "Price Snapshot"

    # Column widths
    ws1.column_dimensions["A"].width = 55
    ws1.column_dimensions["B"].width = 15
    ws1.column_dimensions["C"].width = 20

    # Title
    ws1.merge_cells("A1:C1")
    ws1["A1"] = "PRICE TRACKER — CURRENT SNAPSHOT"
    ws1["A1"].font = Font(name="Calibri", bold=True, size=16, color=WHITE)
    ws1["A1"].fill = PatternFill("solid", fgColor=BG_HEADER)
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 30

    ws1.merge_cells("A2:C2")
    ws1["A2"] = f"Generated: {today}  |  Source: books.toscrape.com"
    ws1["A2"].font = Font(name="Calibri", size=10)
    ws1["A2"].alignment = Alignment(horizontal="center")

    # Headers
    headers = ["Product Title", "Current Price (£)", "Last Scraped"]
    for col, header in enumerate(headers, 1):
        make_header_cell(ws1, 3, col, header)
    ws1.row_dimensions[3].height = 20

    # Data
    prices = get_all_latest_prices()
    normal_font = Font(name="Calibri", size=10)
    border = make_border()

    for i, (title, price, date) in enumerate(prices):
        row = i + 4
        ws1.cell(row=row, column=1, value=title).font = normal_font
        ws1.cell(row=row, column=1).border = border

        price_cell = ws1.cell(row=row, column=2, value=price)
        price_cell.font = normal_font
        price_cell.number_format = "£#,##0.00"
        price_cell.alignment = Alignment(horizontal="center")
        price_cell.border = border

        ws1.cell(row=row, column=3, value=date).font = normal_font
        ws1.cell(row=row, column=3).alignment = Alignment(horizontal="center")
        ws1.cell(row=row, column=3).border = border
        ws1.row_dimensions[row].height = 16

        # Alternating row colors
        if i % 2 == 0:
            for col in range(1, 4):
                ws1.cell(row=row, column=col).fill = PatternFill(
                    "solid", fgColor="F5F7FF")

    # Summary stats
    if prices:
        all_prices = [p[1] for p in prices]
        summary_row = len(prices) + 5
        ws1.merge_cells(f"A{summary_row}:C{summary_row}")
        make_section_cell(ws1, summary_row, 1, "SUMMARY STATISTICS")
        ws1.merge_cells(f"A{summary_row}:C{summary_row}")

        stats = [
            ("Total Products Tracked:", len(prices)),
            ("Average Price:", f"£{sum(all_prices)/len(all_prices):.2f}"),
            ("Highest Price:", f"£{max(all_prices):.2f}"),
            ("Lowest Price:", f"£{min(all_prices):.2f}"),
        ]

        for j, (label, value) in enumerate(stats):
            row = summary_row + j + 1
            cell = ws1.cell(row=row, column=1, value=label)
            cell.font = Font(name="Calibri", bold=True, size=10)
            val_cell = ws1.cell(row=row, column=2, value=value)
            val_cell.font = Font(name="Calibri", size=10)
            val_cell.alignment = Alignment(horizontal="center")

    # =====================
    # SHEET 2 - PRICE DROPS
    # =====================
    ws2 = wb.create_sheet("Price Drops")
    ws2.column_dimensions["A"].width = 55
    ws2.column_dimensions["B"].width = 15
    ws2.column_dimensions["C"].width = 15
    ws2.column_dimensions["D"].width = 15
    ws2.column_dimensions["E"].width = 15

    ws2.merge_cells("A1:E1")
    ws2["A1"] = "PRICE DROP ALERTS"
    ws2["A1"].font = Font(name="Calibri", bold=True, size=16, color=WHITE)
    ws2["A1"].fill = PatternFill("solid", fgColor=BG_HEADER)
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 30

    ws2.merge_cells("A2:E2")
    ws2["A2"] = "Products where price has dropped 5% or more across scrape sessions"
    ws2["A2"].font = Font(name="Calibri", size=10)
    ws2["A2"].alignment = Alignment(horizontal="center")

    drop_headers = ["Product Title", "Low Price (£)",
                    "High Price (£)", "Drop Amount (£)", "Drop %"]
    for col, header in enumerate(drop_headers, 1):
        make_header_cell(ws2, 3, col, header)

    drops = get_price_drops(threshold_pct=5.0)
    if drops:
        for i, (title, low, high, amount, pct) in enumerate(drops):
            row = i + 4
            ws2.cell(row=row, column=1, value=title).font = normal_font
            ws2.cell(row=row, column=1).border = border
            for col, val in enumerate([low, high, amount], 2):
                cell = ws2.cell(row=row, column=col, value=val)
                cell.font = normal_font
                cell.number_format = "£#,##0.00"
                cell.alignment = Alignment(horizontal="center")
                cell.border = border
                cell.fill = PatternFill("solid", fgColor=BG_ALERT)
            pct_cell = ws2.cell(row=row, column=5, value=f"{pct}%")
            pct_cell.font = Font(name="Calibri", bold=True, size=10,
                                  color="CC0000")
            pct_cell.alignment = Alignment(horizontal="center")
            pct_cell.border = border
            pct_cell.fill = PatternFill("solid", fgColor=BG_ALERT)
    else:
        ws2.merge_cells("A4:E4")
        ws2["A4"] = "No price drops detected yet — run scraper across multiple days to track changes"
        ws2["A4"].font = Font(name="Calibri", italic=True, size=10)
        ws2["A4"].alignment = Alignment(horizontal="center")

    # =====================
    # SHEET 3 - TOP RATED
    # =====================
    ws3 = wb.create_sheet("Analytics")
    ws3.column_dimensions["A"].width = 30
    ws3.column_dimensions["B"].width = 20

    ws3.merge_cells("A1:B1")
    ws3["A1"] = "PRICE DISTRIBUTION"
    ws3["A1"].font = Font(name="Calibri", bold=True, size=14, color=WHITE)
    ws3["A1"].fill = PatternFill("solid", fgColor=BG_HEADER)
    ws3["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws3.row_dimensions[1].height = 25

    # Price buckets
    if prices:
        all_prices = [p[1] for p in prices]
        buckets = {
            "Under £10": len([p for p in all_prices if p < 10]),
            "£10 - £20": len([p for p in all_prices if 10 <= p < 20]),
            "£20 - £30": len([p for p in all_prices if 20 <= p < 30]),
            "£30 - £40": len([p for p in all_prices if 30 <= p < 40]),
            "£40 - £50": len([p for p in all_prices if 40 <= p < 50]),
            "Over £50": len([p for p in all_prices if p >= 50]),
        }

        make_header_cell(ws3, 2, 1, "Price Range")
        make_header_cell(ws3, 2, 2, "Number of Products")

        for i, (bucket, count) in enumerate(buckets.items()):
            row = i + 3
            ws3.cell(row=row, column=1, value=bucket).font = normal_font
            ws3.cell(row=row, column=1).border = border
            count_cell = ws3.cell(row=row, column=2, value=count)
            count_cell.font = normal_font
            count_cell.alignment = Alignment(horizontal="center")
            count_cell.border = border

        # Bar chart
        chart = BarChart()
        chart.type = "col"
        chart.title = "Price Distribution"
        chart.y_axis.title = "Number of Products"
        chart.x_axis.title = "Price Range"
        chart.style = 10
        chart.width = 15
        chart.height = 10

        data = Reference(ws3, min_col=2, min_row=2,
                         max_row=2 + len(buckets))
        cats = Reference(ws3, min_col=1, min_row=3,
                         max_row=2 + len(buckets))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        ws3.add_chart(chart, "D2")

    # Save
    filename = os.path.join(BASE_DIR, f"PriceReport_{today}.xlsx")
    wb.save(filename)
    print(f"\nReport saved as: {filename}")
    return filename


if __name__ == "__main__":
    build_report()