from PIL import Image

def resize_by_duplication(input_path, output_path, scale=4):
    # Resmi aç
    img = Image.open(input_path)

    # Yeni boyutları hesapla
    new_width = img.width * scale
    new_height = img.height * scale

    # Pixel çoğaltarak büyüt (NEAREST)
    resized_img = img.resize((new_width, new_height), Image.NEAREST)

    # Kaydet
    resized_img.save(output_path)
    print(f"Resim büyütüldü ve kaydedildi: {output_path}")
