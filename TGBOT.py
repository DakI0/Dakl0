import logging
import telebot
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Создаем объект бота
bot = telebot.TeleBot("7854448950:AAFZ0_9KWLpY2bRC8lTCDvkZZ5iOekH7H7I")

# Приветствие и рассказ о функциях
@bot.message_handler(commands=['start'])
def start(message):
    logger.info("Получена команда /start от пользователя.")
    bot.send_message(
        message.chat.id,
        "Привет! Я ассистент для молодых ученых.\n"
        "Мои функции:\n"
        "1. Перевод частоты излучения/энергии фотона в длину волны и обратно (/convert_frequency).\n"
        "   Введите: /convert_frequency тип значение (например, /convert_frequency frequency 5e14).\n"
        "2. Анализ спектра (/analyze_spectrum).\n"
        "   Введите: /analyze_spectrum, чтобы начать анализ. Я попрошу вас ввести данные для анализа.\n"
        "3. Вычисление флюенса лазера (/calculate_fluence).\n"
        "   Введите: /calculate_fluence мощность частота площадь (например, /calculate_fluence 10 1e9 0.01).\n"
        "4. Опрос о качестве работы (/feedback).\n"
        "   Введите: /feedback и напишите ваш отзыв.\n"
        "Пожалуйста, используйте команды для взаимодействия."
    )

# Конвертация частоты или энергии в длину волны
@bot.message_handler(commands=['convert_frequency'])
def convert_frequency(message):
    try:
        logger.info("Обработка запроса на конвертацию частоты/энергии.")
        args = message.text.split()[1:]
        if len(args) != 2:
            bot.reply_to(message, "Введите два аргумента: тип ('frequency' или 'energy') и значение.\n"
                                  "Пример: /convert_frequency frequency 5e14")
            return

        type_of_input = args[0].lower()
        value = float(args[1])

        h = 6.62607015e-34  # Дж·с
        c = 299792458       # м/с

        if type_of_input == "frequency":
            wavelength = c / value
            bot.reply_to(message, f"Длина волны: {wavelength:.2e} м")
        elif type_of_input == "energy":
            wavelength = h * c / value
            bot.reply_to(message, f"Длина волны: {wavelength:.2e} м")
        else:
            bot.reply_to(message, "Тип должен быть 'frequency' или 'energy'.")
    except Exception as e:
        logger.error("Ошибка при обработке запроса на конвертацию: %s", e)
        bot.reply_to(message, f"Ошибка: {e}")

# Анализ спектра для нахождения пика и его ширины на полувысоте
@bot.message_handler(commands=['analyze_spectrum'])
def request_spectrum_data(message):
    bot.send_message(message.chat.id, "Введите данные для анализа спектра. Например, можно просто начать анализ, "
                                        "нажав /analyze_spectrum.")
    bot.register_next_step_handler(message, analyze_spectrum)

def analyze_spectrum(message):
    try:
        # Пример данных для анализа
        wavelengths = np.linspace(400, 700, 100)
        intensities = np.sin(wavelengths) + np.random.normal(0, 0.1, len(wavelengths))

        peaks, _ = find_peaks(intensities, height=0)
        peak_wavelength = wavelengths[peaks][0]
        fwhm = np.abs(peak_wavelength - wavelengths[peaks][-1])

        plt.plot(wavelengths, intensities)
        plt.axvline(peak_wavelength, color='r', linestyle='--', label=f'Peak: {peak_wavelength:.2f} nm')
        plt.axvline(peak_wavelength - fwhm/2, color='g', linestyle='--', label='FWHM Start')
        plt.axvline(peak_wavelength + fwhm/2, color='g', linestyle='--', label='FWHM End')
        plt.legend()
        plt.title("Анализ спектра")
        plt.xlabel("Длина волны (нм)")
        plt.ylabel("Интенсивность")

        plt.savefig('spectrum_analysis.png')
        plt.close()

        with open('spectrum_analysis.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        bot.reply_to(message, f"Пик на длине волны {peak_wavelength:.2f} нм, ширина на полувысоте {fwhm:.2f} нм.")
    except Exception as e:
        logger.error("Ошибка при анализе спектра: %s", e)
        bot.reply_to(message, f"Ошибка: {e}")

# Вычисление флюенса
@bot.message_handler(commands=['calculate_fluence'])
def calculate_fluence(message):
    try:
        logger.info("Обработка запроса на вычисление флюенса.")
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.reply_to(message, "Введите три аргумента: мощность (Вт), частота (Гц), площадь (м²).\n"
                                  "Пример: /calculate_fluence 10 1e9 0.01")
            return

        power = float(args[0])
        frequency = float(args[1])
        area = float(args[2])

        fluence = power / (frequency * area)
        bot.reply_to(message, f"Флюенс: {fluence:.2e} Дж/м²")
    except Exception as e:
        logger.error("Ошибка при вычислении флюенса: %s", e)
        bot.reply_to(message, f"Ошибка: {e}")

# Опрос о качестве работы бота
@bot.message_handler(commands=['feedback'])
def feedback(message):
    logger.info("Получен отзыв.")
    bot.reply_to(message, "Спасибо за ваш отзыв! Мы учтем ваше мнение.\n"
                          "Если у вас есть еще предложения, напишите их.")
    # Дополнительный ответ на отзыв
    response_text = "Ваш отзыв был зарегистрирован. Если есть предложения, дайте знать!"
    bot.send_message(message.chat.id, response_text)

# Запуск бота
logger.info("Запуск бота...")
bot.polling()
