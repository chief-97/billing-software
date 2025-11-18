import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ========== DATABASE CONNECTION ==========
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="SHIVAM97",
    database="shop"
)
cursor = conn.cursor()

def print_invoice_header():
    print("\n" + "="*45)
    print("         🧾 CHIEF STORE INVOICE 🧾")
    print("="*45 + "\n")

def print_invoice_footer(grand_total):
    print("-"*45)
    print(f"{'Grand Total:':<35} ₹{grand_total:>8.2f}")
    print("="*45)
    print("Thank you for shopping with Chief Store!")
    print("="*45 + "\n")

# ========== MAIN PROGRAM LOOP ==========
while True:
    print_invoice_header()
    print("1️⃣  Print New Invoice")
    print("2️⃣  Refer Old Invoice")
    print("3️⃣  Exit Program\n")

    choice = input("Enter your choice (1 / 2 / 3): ").strip()

    # ========== OPTION 1: PRINT NEW INVOICE ==========
    if choice == "1":
        customer_name = input("Enter customer name: ")
        items = []

        while True:
            item = input("Enter item name: ")
            qty = float(input("Enter quantity: "))
            price = float(input("Enter price per item: "))
            total = qty * price
            items.append((item, qty, price, total))

            cont = input("Add more items? (yes/no): ").lower()
            if cont != 'yes':
                break

        grand_total = sum(x[3] for x in items)

        cursor.execute(
            "INSERT INTO bill (customer_name, total_amount) VALUES (%s, %s)",
            (customer_name, grand_total)
        )
        bill_id = cursor.lastrowid

        for item in items:
            cursor.execute(
                "INSERT INTO bill_items (bill_id, item_name, quantity, price, total) VALUES (%s, %s, %s, %s, %s)",
                (bill_id, item[0], item[1], item[2], item[3])
            )
        conn.commit()

        # ========== PRINT INVOICE ==========
        print_invoice_header()
        print(f"Bill ID       : {bill_id}")
        print(f"Customer Name : {customer_name}")
        print("-"*45)
        print(f"{'Item':<18}{'Qty':<8}{'Price':<9}{'Total':>8}")
        print("-"*45)

        for item in items:
            print(f"{item[0]:<18}{item[1]:<8}{item[2]:<9}₹{item[3]:>7.2f}")

        print_invoice_footer(grand_total)

        # ========== EMAIL SENDING ==========
        send_mail = input("Send full invoice via Email? (yes/no): ").lower()
        if send_mail == "yes":
            sender = "your_email@gmail.com"
            password = "your_app_password"
            receiver = input("Enter customer's email: ")

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Invoice from Chief Store (Bill ID: {bill_id})"
            msg["From"] = sender
            msg["To"] = receiver

            bill_text = f"Hello {customer_name},\n\nHere is your invoice (Bill ID: {bill_id}):\n\n"
            bill_text += f"{'Item':<15}{'Qty':<10}{'Price':<10}{'Total'}\n"
            bill_text += "-" * 45 + "\n"

            for item in items:
                bill_text += f"{item[0]:<15}{item[1]:<10}{item[2]:<10}{item[3]}\n"

            bill_text += "-" * 45 + f"\nGrand Total: ₹{grand_total}\n\nThank you for shopping with Chief Store!"

            msg.attach(MIMEText(bill_text, "plain"))

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender, password)
                    server.sendmail(sender, receiver, msg.as_string())
                print("✅ Bill sent successfully via Email!")
            except Exception as e:
                print(f"❌ Email sending failed: {e}")

    # ========== OPTION 2: REFER OLD INVOICE ==========
    elif choice == "2":
        search_name = input("Enter customer name to search invoice: ")

        cursor.execute(
            "SELECT bill_id, total_amount, customer_name FROM bill WHERE LOWER(customer_name) = LOWER(%s)",
            (search_name,)
        )
        bills = cursor.fetchall()

        if not bills:
            print(f"\n❌ No invoice found for customer '{search_name}'.")
        else:
            for bill in bills:
                bill_id = bill[0]
                total_amount = bill[1]
                customer_name = bill[2]

                print_invoice_header()
                print(f"Bill ID       : {bill_id}")
                print(f"Customer Name : {customer_name}")
                print("-"*45)
                print(f"{'Item':<18}{'Qty':<8}{'Price':<9}{'Total':>8}")
                print("-"*45)

                cursor.execute(
                    "SELECT item_name, quantity, price, total FROM bill_items WHERE bill_id = %s",
                    (bill_id,)
                )
                items = cursor.fetchall()

                for item in items:
                    print(f"{item[0]:<18}{item[1]:<8}{item[2]:<9}₹{item[3]:>7.2f}")

                print_invoice_footer(total_amount)

    # ========== EXIT ==========
    elif choice == "3":
        print("\n👋 Exiting Chief Store Billing System... Goodbye!\n")
        break

    else:
        print("❌ Invalid option selected!")

# ========== CLOSE CONNECTION ==========
conn.close()
