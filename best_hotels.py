import math
import requests
from bs4 import BeautifulSoup
from tkinter import *
from tkcalendar import DateEntry
from datetime import datetime
from tkinter import END, messagebox
import pandas as pd
from tkinter.ttk import Combobox

class HotelListingGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Best Hotels For You")
        self.master.geometry("700x700")
        self.master.configure(background="#b3e8e4")

        # Load the image
        self.image = PhotoImage(file="C:\\Users\ozlem\PycharmProjects\lab1\indir.png")

        # Create a label for the image
        self.image_label = Label(self.master, image=self.image, bg="#b3e8e4")
        self.image_label.grid(row=0, column=0, columnspan=3, pady=10)


        # List of European cities
        european_cities = [
            "London",
            "Paris",
            "Berlin",
            "Madrid",
            "Rome",
            "Amsterdam",
            "Vienna",
            "Prague",
            "Athens",
            "Stockholm"
        ]



        self.city_combobox = Combobox(self.master,
                                      values=european_cities,
                                      width=20,
                                      state="readonly")
        self.city_combobox.current(0)  # Set default selection
        self.city_combobox.grid(row=1, column=0, pady=10)


        self.select_button = Button(self.master,
                                    text="Select City",
                                    command=self.select_city)
        self.select_button.grid(row=1, column=1, padx=10, pady=10)


        self.check_in_date_entry = DateEntry(self.master, width=12, background='darkblue', foreground='white',
                                             borderwidth=2, date_pattern='yyyy-mm-dd', mindate=datetime.today())
        self.check_in_date_entry.grid(row=2, column=0, padx=10, pady=10)


        self.check_in_button = Button(self.master, text="Select Check-in Date", command=self.select_check_in_date)
        self.check_in_button.grid(row=2, column=1, padx=10, pady=10)


        self.check_out_date_entry = DateEntry(self.master, width=12, background='darkblue', foreground='white',
                                              borderwidth=2, date_pattern='yyyy-mm-dd', mindate=datetime.today())
        self.check_out_date_entry.grid(row=3, column=0, padx=10, pady=10)


        self.check_out_button = Button(self.master, text="Select Check-out Date", command=self.select_check_out_date)
        self.check_out_button.grid(row=3, column=1, padx=10, pady=10)


        self.title_label2 = Label(self.master,
                                  text="Please select euro or tl",
                                  font=("Arial", 13, "bold"),
                                  bg="#b3e8e4")
        self.title_label2.grid(row=4, column=0, columnspan=2, pady=10)


        self.button_frame = Frame(self.master,
                                  bg="#b3e8e4")
        self.button_frame.grid(row=5, column=0, columnspan=2, pady=10)


        self.currency_var = StringVar(value="")


        self.button1 = Radiobutton(self.button_frame, text="TL", variable=self.currency_var, value="TL")
        self.button1.grid(row=0, column=0, padx=10)


        self.button2 = Radiobutton(self.button_frame, text="Euro", variable=self.currency_var, value="EURO")
        self.button2.grid(row=0, column=1)

        self.display_button = Button(self.master, text="Show Top Hotels", command=self.display_top_hotels)
        self.display_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.top_hotels_label = Label(self.master, text="Top 5 Hotels", font=("Helvetica", 16, "bold"),
                                      foreground="green")
        self.top_hotels_label.grid(row=7, column=0, columnspan=2, pady=10)

        self.top_hotels_text = Text(self.master, height=15, width=90)
        self.top_hotels_text.grid(row=8, column=0, columnspan=2, pady=10)

    def select_city(self):
        selected_city = self.city_combobox.get()
        print("Selected city:", selected_city)

    def select_check_in_date(self):
        selected_date = self.check_in_date_entry.get_date()
        print("Check-in date:", selected_date)

    def select_check_out_date(self):
        selected_date = self.check_out_date_entry.get_date()
        print("Check-out date:", selected_date)

    def select_check_out_date(self):
        try:
            selected_check_in_date = self.check_in_date_entry.get_date()
            selected_check_out_date = self.check_out_date_entry.get_date()

            # Ensure check-out date is not before check
            if selected_check_out_date < selected_check_in_date:
                raise ValueError("Check-out date cannot be before the check-in date.")

            print("Check-out date:", selected_check_out_date)

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def display_top_hotels(self):
        city = self.city_combobox.get()
        check_in = self.check_in_date_entry.get()
        check_out = self.check_out_date_entry.get()
        currency = self.currency_var.get()
        top_hotels_df = self.fetch_hotels(city, check_in, check_out, currency)

        print("Type of top_hotels:", type(top_hotels_df))

        # Check if the DataFrame is not empty
        self.top_hotels_text.delete(1.0, END)
        if not top_hotels_df.empty:
            for index, row in top_hotels_df.iterrows():
                self.top_hotels_text.insert(END,
                                            f"{row['title']}\nAddress: {row['address']}\nDistance: {row['distance']}\nRating: {row['rating']}\nPrice: {row['price']} {currency}\n\n")
        else:
            # If no hotels were found, display a message
            self.top_hotels_text.insert(END, "No hotels found for the selected criteria.")
        # Store the fetched hotel data in a CSV file
        self.store_hotel_data(top_hotels_df)

    def fetch_hotels(self, city, check_in, check_out, currency):
        top_hotels_data = []

        try:
            url = self.get_url(city, check_in, check_out)
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            hotels = soup.find_all('div', {'data-testid': 'property-card'})

            for hotel in hotels[:10]:  # Fetch data for the first 10 hotels
                # Extract hotel information
                name_element = hotel.find('div', {'data-testid': 'title'})
                name = name_element.text.strip() if name_element else "NOT GIVEN"
                address_element = hotel.find('span', {'data-testid': 'address'})
                address = address_element.text.strip() if address_element else "NOT GIVEN"
                distance_element = hotel.find('span', {'data-testid': 'distance'})
                distance = distance_element.text.strip() if distance_element else "NOT GIVEN"
                rating_element = hotel.find('span', {'class': 'a3332d346a'})
                rating_str = rating_element.text.strip() if rating_element else "Rating not available"

                price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
                price_str = price_element.text.strip() if price_element else "NOT GIVEN"

                # Extract numerical value from price string and remove commas
                price_value = price_str.split()[1].replace(',', '')
                price_tl = float(price_value)

                # Convert TL to EURO if currency is EURO
                if currency == 'EURO':
                    price_tl = math.floor(price_tl / 30)

                top_hotels_data.append({
                    'title': name,
                    'address': address,
                    'distance': distance,
                    'rating': rating_str,
                    'price': price_tl
                })

        except Exception as e:
            print("Error occurred:", str(e))


        top_hotels_df = pd.DataFrame(top_hotels_data)

        if not top_hotels_df.empty:

            top_hotels_df = top_hotels_df.sort_values(by='rating', ascending=False,
                                                      key=lambda x: pd.to_numeric(x.str.extract(r'(\d+\.\d+|\d+)')[0],
                                                                                  errors='coerce')).head(5)

        return top_hotels_df

    def get_url(self, city, check_in, check_out):
        city_id = cities.get(city, "")
        base_url = 'https://www.booking.com/searchresults.html?ss={city}&ssne={city}&ssne_untouched={city}&efdco=1&label=gen173nr-1FCAEoggI46AdIM1gEaOQBiAEBmAExuAEHyAEP2AEB6AEBAECiAIBqAIDuAKo8sKxBsACAdICJGZlZWVmNGJjLWI2OGEtNGM0OS05ODk0LTM2ZGQ4YzkxYzY0MNgCBeACAQ&aid=304142&lang=en-us&sb=1&src_elem=sb&src=index&dest_id={city_id}&dest_type=city&checkin={check_in}&checkout={check_out}&group_adults=2&no_rooms=1&group_children=0'
        return base_url.format(city=city, city_id=city_id, check_in=check_in, check_out=check_out)

    def store_hotel_data(self, hotels):
        try:
            hotels.to_csv('myhotels.csv', header=True, index=False)
            messagebox.showinfo("Success", "Hotel data successfully stored in CSV file.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while storing hotel data: {str(e)}")
            print("Error occurred while storing hotel data:", str(e))


# Dictionary mapping city names to their IDs
cities = {
    "London": "-2601889",
    "Paris": "-1456928",
    "Berlin": "-1746443",
    "Madrid": "-390625",
    "Rome": "-126693",
    "Amsterdam": "-2140479",
    "Vienna": "-1995499",
    "Prague": "-1476801",
    "Athens": "-814876",
    "Stockholm": "-2524279"
}

if __name__ == "__main__":
    root = Tk()
    hotel_listing_gui = HotelListingGUI(root)
    root.mainloop()
