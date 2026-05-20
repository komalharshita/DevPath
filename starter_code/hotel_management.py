"""
hotel_management.py
===================
Project:    Sunrise Grand Hotel Management System
Type:       CLI (Command Line Interface)
Difficulty: Medium
Skills:     Python, Dictionaries, Functions, Error Handling, Input Validation
Time:       Medium (a weekend)

What you will build:
    A robust hotel management application to manage a 40-room inventory 
    across four categories. The system allows for dynamic room 
    initialization, guest booking with automatic price calculation 
    based on stay duration, booking cancellations, and targeted 
    searches by room category.

How to run:
    python hotel_management.py    

Learning goals:
    - Managing state using nested dictionaries and lists.
    - Implementing robust input validation for user data.
    - Structuring a menu-driven CLI application.
    - Handling basic business logic (billing, availability).

Roadmap:
    Step 1: Initialize the 40-room inventory with tiered pricing.
    Step 2: Implement availability display and category filtering.
    Step 3: Build the booking engine with contact validation.
    Step 4: Create the cancellation and guest detail lookup logic.
    Step 5: Wrap all logic in a persistent main menu loop.
"""
# ---------------------------------------------------------------------------
# Core Logic & Initialization
# ---------------------------------------------------------------------------

def initialize_rooms():
    """
    Initializes a 40-room inventory across four distinct luxury categories.
    Deluxe: 101-110 (Rs. 2500)| Super Deluxe: 201-210 (Rs. 3500)| Suite: 301-310 (Rs. 5000)| Presidential: 401-410 (Rs. 8000)
    """
    rooms = {}
    
    # Configuration Mapping: {Floor/Base: (Category Name, Nightly Rate)}
    config = {
        100: ("Deluxe", 2500),
        200: ("Super Deluxe", 3500),
        300: ("Suite", 5000),
        400: ("Presidential Suite", 8000)
    }

    # Nested loop to generate 10 rooms per floor based on configuration
    for base_no, (room_type, price) in config.items():
        for i in range(1, 11):
            room_no = base_no + i
            # Structure: [Type, Price, Status, Guest_Data_Dict]
            rooms[room_no] = [room_type, price, "Available", None]
            
    return rooms

# Instantiate the global room database
rooms = initialize_rooms()

# ---------------------------------------------------------------------------
# Room Management Functions
# ---------------------------------------------------------------------------

def show_available_rooms():
    """Filters and displays only the rooms currently marked as 'Available'."""
    print("\n--- 1. Available Rooms ---")
    found = False
    for room_no, details in rooms.items():
        if details[2] == "Available":
            print(f"Room No: {room_no} | Type: {details[0]} | Price/Day: Rs. {details[1]}")
            found = True
    if not found:
        print(">> No rooms currently available.")

def book_room():
    """
    Handles the end-to-end booking process. 
    Includes input validation for contact numbers and stay duration limits.
    """
    show_available_rooms()
    
    try:
        room_no = int(input("\nEnter room number to book: "))
    except ValueError:
        print(">> Invalid input. Please enter a numerical room number.")
        return

    # Check if room exists in the initialized database
    if room_no not in rooms:
        print(">> Error: Invalid room number.")
        return

    # Prevent double-booking of occupied rooms
    if rooms[room_no][2] == "Booked":
        print(">> Room is already occupied. Please select another.")
        return
    
    print(f"\nBooking Room {room_no} ({rooms[room_no][0]} @ Rs. {rooms[room_no][1]}/day)")
    name = input("Enter Guest Name: ").strip()
    contact = input("Enter Contact Number: ").strip()
    
    # Validation loop for a standard 10-digit mobile number
    while len(contact) != 10 or not contact.isdigit():
        print(">> Error: Contact number must be exactly 10 digits.")
        contact = input("Enter Contact Number: ").strip()

    try:
        days = int(input("Enter Number of Days of Stay: "))
        if days <= 0:
            print(">> Error: Duration must be at least 1 day.")
            return
        # Enforcing a 30-day policy to prevent long-term squatting without review
        elif days > 30:
            while days > 30:
                print(">> Error: Policy Limit! Maximum initial stay is 30 days.")
                days = int(input("Enter Number of Days of Stay: "))
    except ValueError:
        print(">> Invalid input. Please enter numbers only for the duration.")
        return
        
    # Automatic calculation of total billing
    price_per_day = rooms[room_no][1]
    total_price = price_per_day * days

    # Commit booking data to the dictionary
    rooms[room_no][2] = "Booked"
    rooms[room_no][3] = {
        "Guest Name": name,
        "Contact": contact,
        "Days": days,
        "Total Price": total_price
    }

    print("\n✅ Room booked successfully!")
    print(f"Total Amount to Pay: Rs. {total_price}") 

def cancel_booking():
    """Resets a booked room back to 'Available' status and clears guest data."""
    try:
        room_no = int(input("Enter room number to cancel: "))
    except ValueError:
        print(">> Invalid input.")
        return

    if room_no in rooms and rooms[room_no][2] == "Booked":
        rooms[room_no][2] = "Available"
        rooms[room_no][3] = None
        print(f"✅ Booking for Room {room_no} cancelled. Room is now vacant.")
    else:
        print(f">> Room {room_no} is not currently booked.")

# ---------------------------------------------------------------------------
# Search & Reporting Functions
# ---------------------------------------------------------------------------        

def search_by_type():
    """Allows filtering of the entire inventory by specific room categories."""
    print("\nCategories: Deluxe, Super Deluxe, Suite, Presidential Suite")
    room_type_search = input("Enter Room Type to filter: ").strip().lower()
    
    found = False
    for room_no, details in rooms.items():
        if details[0].lower() == room_type_search:
            status = details[2]
            # Ternary-style logic for guest display
            guest = f"({details[3]['Guest Name']})" if status == "Booked" else ""
            print(f"Room No: {room_no} | Status: {status} {guest} | Price/Day: Rs. {details[1]}")
            found = True

    if not found:
        print(f">> No rooms found for category: {room_type_search.title()}")

def view_guest_details():
    """Provides a detailed billing and contact breakdown for a specific room."""
    try:
        room_no = int(input("Enter room number: "))
    except ValueError:
        return

    if room_no in rooms and rooms[room_no][2] == "Booked":
        guest = rooms[room_no][3]
        print(f"\n--- Guest Details for Room {room_no} ---")
        print(f"Name: {guest['Guest Name']}")
        print(f"Contact: {guest['Contact']}")
        print(f"Stay Duration: {guest['Days']} days")
        print(f"Total Billing: Rs. {guest['Total Price']} (Rs .{rooms[room_no][1]} x {guest['Days']})")
    else:
        print(">> No active booking found for this room.")

# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def main_menu():
    """The central control hub for the Management System."""
    while True:
        print("\n" + "="*45)
        print("   SUNRISE GRAND HOTEL MANAGEMENT SYSTEM")
        print("="*45)
        print("1. Show Available Rooms\n2. Book a Room\n3. Cancel Booking")
        print("4. Search Rooms by Type\n5. View Guest Details\n6. Exit")
        
        choice = input("\nSelect an option (1-6): ").strip()

        if choice == '1': show_available_rooms()
        elif choice == '2': book_room()
        elif choice == '3': cancel_booking()
        elif choice == '4': search_by_type()
        elif choice == '5': view_guest_details()
        elif choice == '6':
            print("\n👋 System Shutdown. Have a professional day!")
            break
        else:
            print("❌ Invalid selection.")

if __name__ == "__main__":
    main_menu()
