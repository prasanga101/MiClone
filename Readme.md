# MiClone

A personal AI bot that texts like you.

## What it does
- Monitors your Messenger and Instagram DMs in real-time
- Scrapes your past messages to learn your texting style
- Stores all data in Supabase
- Uses a custom fine-tuned LLM to reply as you
- Handles Romanized Nepali (Nepali written in English letters)
- Only responds to new messages — never touches past chats

## Tech Stack
- Python + Selenium → real-time message monitoring
- Supabase → message storage
- MLX + Fine-tuned LLM → style learning & reply generation
- Oracle Cloud → 24/7 server hosting

## Structure
config/       → environment & settings
database/     → Supabase connection & queries
scrapers/     → Selenium scrapers for Messenger & Instagram
pipeline/     → data collection & message monitoring
model/        → LLM style extraction & inference