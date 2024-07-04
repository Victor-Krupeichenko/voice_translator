import os
import playsound
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator


class SpeechTranslator:
    """
    Класс распознания речи пользователя полученной с микрофона, а также переводит распознанную речь на указанный язык.
    Воспроизводит перевод в слух.
    """

    def __init__(self, user_language='ru', translate_language='en', voice_file_name='translated_text.mp3', mic_idx=1):
        """
        :param user_language: Язык, на котором говорит пользователь. По умолчанию 'ru'
        :param translate_language: Язык, на который нужно перевести речь. По умолчанию 'en'.
        :param voice_file_name: Имя файла, в который будет сохранен перевод. По умолчанию 'translated_text.mp3'
        """
        self.user_language = user_language
        self.translate_language = translate_language
        self.voice_file_name = voice_file_name
        self.__words_exit = ('exit', 'выход')  # слова, которые признаны как выход из приложения
        self.recognizer = sr.Recognizer()
        self.translator = Translator()
        self.microphone = sr.Microphone(device_index=mic_idx)

    def get_voice(self):
        """
        Получает с микрофона речь пользователя и возвращает ее текст.
        :return: Текст речи пользователя
        """

        with self.microphone as source:
            self.recognizer.energy_threshold = 800
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            print('Слушаю вас...')
            voice_text = self.recognizer.listen(source)
            try:
                recognized_text = self.recognizer.recognize_google(voice_text, language=self.user_language)
                if not recognized_text:
                    return None
                print(f'Исходный текст: {recognized_text}')
                return recognized_text
            except sr.UnknownValueError:
                print('Распознавание речи Google не может распознать звук')
            except sr.RequestError as exc:
                print(f'Не удалось запросить результаты от службы распознавания речи Google {exc}')

    def translate_text(self, recognized_text):
        """
        Переводит текст.
        :param recognized_text: Текст который нужно перевести
        :return: Переведенный текст
        """
        try:
            translated_text = self.translator.translate(recognized_text, dest=self.translate_language).text
            if not translated_text:
                return None
            print(f'Перевод на {self.translate_language}: {translated_text}')
            return translated_text
        except Exception as exc:
            print(f'Ошибка при переводе: {exc}')

    def save_voice_file(self, translated_text):
        """
        Сохраняет mp3-файл с переведенным текстом.
        :param translated_text: Текст который нужно сохранить в mp3-файл
        """
        if not translated_text:
            return
        try:
            gtts = gTTS(text=translated_text, lang=self.translate_language, slow=False)
            gtts.save(self.voice_file_name)
        except Exception as exc:
            print(f'Ошибка при сохранении mp3-файла: {exc}')

    def plays_file(self):
        """
        Воспроизводит mp3-файл с переведенным текстом и удаляет этот файл.
        """
        try:
            if os.path.exists(self.voice_file_name):
                playsound.playsound(self.voice_file_name)
                os.remove(self.voice_file_name)
                return
            print('Файл с переведенным текстом не найден')
        except Exception as exc:
            print(f'Ошибка при воспроизведении файла: {exc}')

    def start_program(self):
        """
        Запускает программу и вызывает все необходимы для работы программы методы
        """
        while True:
            recognized_text = self.get_voice()
            if not recognized_text:
                continue
            if len(recognized_text) <= 5 and recognized_text[:5].lower() in self.__words_exit:
                print('Выхожу')
                break
            translated_text = self.translate_text(recognized_text)
            self.save_voice_file(translated_text)
            self.plays_file()


if __name__ == '__main__':
    translator = SpeechTranslator()
    translator.start_program()
