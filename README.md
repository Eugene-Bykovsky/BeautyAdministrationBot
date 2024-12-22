# Booking Bot

A Telegram bot built with the Aiogram framework for scheduling appointments and viewing salon information. The bot enables users to:

- Book appointments with favorite masters.
- View available salons and their phone numbers.
- Schedule services at specific salons.

## Features

### Handlers Overview

#### Master Booking (`handlers_master.py`)
- **State Management**: FSM (Finite State Machine) states for booking appointments with favorite masters.
- **APIs Used**: Fetch specialists, schedules, and services from external APIs.
- **Key Features**:
  - Select a master and available time slots.
  - Choose services and finalize booking with phone number input.

#### Phone List (`handlers_phone.py`)
- **APIs Used**: Retrieve salon contact numbers.
- **Key Features**:
  - Display salon phone numbers with addresses.
  - Provide callback options for detailed interaction.

#### Salon Booking (`handlers_salon.py`)
- **State Management**: FSM states for scheduling services at specific salons.
- **APIs Used**: Fetch salon details, available services, and schedules.
- **Key Features**:
  - Select salons and services.
  - Finalize appointment with schedule and phone number input.

## Getting Started

### Prerequisites
- Python 3.10+
- Telegram Bot API Token (obtained from [BotFather](https://core.telegram.org/bots#botfather))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Eugene-Bykovsky/BeautyAdministrationBot.git
   cd booking-bot
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure the bot:
   - Create a `.env` file in the root directory with the following content:
     ```env
     TELEGRAM_BOT_TOKEN=your_telegram_bot_token
     API_URL=your_api_url
     ```

### Running the Bot

Run the bot using the following command:
```bash
python run.py
```