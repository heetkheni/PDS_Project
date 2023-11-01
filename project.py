import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # Import Image and ImageTk from PIL
import requests
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CoinGeckoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CoinGecko App")

        # Create and set up GUI components
        self.create_widgets()

        # Initialize the figure and axes for the graph
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

    def create_widgets(self):
        # Label and Combobox for selecting a cryptocurrency
        label = tk.Label(self.root, text="Select Cryptocurrency:")
        label.pack(pady=10)

        # Using ttk.Combobox for a dropdown-like combobox with autocompletion
        self.crypto_combobox = ttk.Entry(self.root)
        self.crypto_combobox.pack(pady=10)

        # Modern-style Button for fetching and displaying data
        fetch_button = ttk.Button(self.root, text="Fetch Data and Show Graph", command=self.fetch_data_and_show_graph)
        fetch_button.pack(pady=10)

        # Display area for showing the fetched data
        self.result_label = tk.Label(self.root, text="", justify="left")
        self.result_label.pack(pady=10)

        # Label for displaying the cryptocurrency image
        self.crypto_image_label = tk.Label(self.root)
        self.crypto_image_label.pack(pady=10)

    def get_crypto_symbols(self):
        # Fetch a list of cryptocurrency symbols
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return [crypto["symbol"] for crypto in data]
        else:
            return []

    def fetch_data_and_show_graph(self):
        # Fetch data and show both data and graph
        entered_crypto = self.crypto_combobox.get()

        if entered_crypto:
            url_info = f"https://api.coingecko.com/api/v3/coins/{entered_crypto.lower()}"
            response_info = requests.get(url_info)

            url_chart = f"https://api.coingecko.com/api/v3/coins/{entered_crypto.lower()}/market_chart"
            params = {"vs_currency": "usd", "days": "7"}  # Adjust parameters as needed
            response_chart = requests.get(url_chart, params=params)

            if response_info.status_code == 200 and response_chart.status_code == 200:
                # Display information
                data_info = response_info.json()
                important_data = {
                    "Name": data_info["name"],
                    "Symbol": data_info["symbol"],
                    "Current Price (USD)": f"$ {data_info['market_data']['current_price']['usd']}",
                    "Market Cap (USD)": f"$ {data_info['market_data']['market_cap']['usd']}",
                    "24h Change (%)": data_info['market_data']['price_change_percentage_24h'],
                    "Total Supply": data_info['market_data']['total_supply'],
                    "Circulating Supply": data_info['market_data']['circulating_supply'],
                    "All-Time High (USD)": f"$ {data_info['market_data']['ath']['usd']}",
                }

                result_text = "\n".join([f"{key}: {value}" for key, value in important_data.items()])
                self.result_label.config(text=result_text)

                # Display the image
                self.display_crypto_image(data_info["image"]["small"])

                # Display the graph
                chart_data = response_chart.json()
                x = [item[0] for item in chart_data["prices"]]
                y = [item[1] for item in chart_data["prices"]]

                self.ax.clear()  # Clear the previous plot
                self.ax.plot(x, y, label='Price Data', linestyle='-')
                self.ax.set_xlabel('Time')
                self.ax.set_ylabel('Price (USD)')
                self.ax.set_title(f'Price Chart for {entered_crypto.upper()}')
                self.ax.legend()

                # Redraw the canvas
                self.canvas.draw()

            else:
                messagebox.showerror("Error", "Error fetching data. Please try again.")
        else:
            self.result_label.config(text="Please select a cryptocurrency symbol.")

    def display_crypto_image(self, image_url):
        # Fetch the image and display it in the label
        response = requests.get(image_url, stream=True)

        if response.status_code == 200:
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((100, 100), Image.ADAPTIVE)  # Resize the image as needed
            photo = ImageTk.PhotoImage(img)
            self.crypto_image_label.config(image=photo)
            self.crypto_image_label.image = photo
        else:
            messagebox.showerror("Error", "Error fetching image. Please try again.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CoinGeckoApp(root)
    root.mainloop()
