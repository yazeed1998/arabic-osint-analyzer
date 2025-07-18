from deep_translator import GoogleTranslator
import pandas as pd
import os

def translate_arabic_csv(input_file, output_file):
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    # Load scraped Arabic data
    df = pd.read_csv(input_file)

    # Translate Arabic titles to English
    translator = GoogleTranslator(source='ar', target='en')
    df['title_en'] = df['title'].apply(lambda x: translator.translate(x))

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    # Save translated data
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ Translated file saved to {output_file}")

if __name__ == "__main__":
    input_csv = 'data/raw/aljazeera_arabic.csv'
    output_csv = 'data/processed/aljazeera_translated.csv'
    translate_arabic_csv(input_csv, output_csv)

