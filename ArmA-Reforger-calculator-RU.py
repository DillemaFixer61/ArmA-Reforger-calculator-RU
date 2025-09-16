from database import mortars
import bisect
import os
import datetime
from colorama import init, Fore, Back, Style

# Инициализация colorama для цветного вывода
init(autoreset=True)

class MortarCalculator:
    def __init__(self):
        self.history = []
        
    def find_closest_keys(self, distances, target_dist):
        """Находит ближайшие ключи расстояний для интерполяции"""
        sorted_dists = sorted(distances.keys())
        if not sorted_dists:
            return None, None, "Нет данных для расчета"
        
        # Проверяем границы диапазона
        if target_dist < sorted_dists[0]:
            min_dist = sorted_dists[0]
            return None, None, f"Слишком малая дистанция. Минимальная: {min_dist}м (не хватает {min_dist - target_dist}м)"
        
        if target_dist > sorted_dists[-1]:
            max_dist = sorted_dists[-1]
            return None, None, f"Слишком большая дистанция. Максимальная: {max_dist}м (превышение на {target_dist - max_dist}м)"
        
        index = bisect.bisect_left(sorted_dists, target_dist)
        
        if index == 0:
            return sorted_dists[0], sorted_dists[0], None
        
        low = sorted_dists[index - 1]
        high = sorted_dists[index]
        
        return low, high, None

    def interpolate(self, low_dist, high_dist, target_dist, low_value, high_value):
        """Линейная интерполяция значений"""
        if low_dist == high_dist:
            return low_value
        ratio = (target_dist - low_dist) / (high_dist - low_dist)
        return low_value + (high_value - low_value) * ratio

    def get_input(self, message, input_type=str, min_val=None, max_val=None, default=None):
        """Универсальная функция ввода данных"""
        while True:
            try:
                if default is not None:
                    prompt = f"{message} [по умолчанию: {default}]: "
                else:
                    prompt = f"{message}: "
                
                print(Fore.CYAN + prompt, end="")
                user_input = input().strip()
                
                if not user_input and default is not None:
                    return default
                
                # Для числовых значений преобразуем, для строк оставляем как есть
                if input_type in [int, float]:
                    value = input_type(user_input)
                else:
                    value = user_input
                
                if min_val is not None and input_type in [int, float] and value < min_val:
                    print(Fore.RED + f"Значение должно быть не меньше {min_val}")
                    continue
                if max_val is not None and input_type in [int, float] and value > max_val:
                    print(Fore.RED + f"Значение должно быть не больше {max_val}")
                    continue
                    
                return value
                
            except ValueError:
                print(Fore.RED + f"Пожалуйста, введите корректное значение")
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\nПрограмма прервана пользователем")
                exit()

    def clear_screen(self):
        """Очищает экран консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, text):
        """Выводит красивый заголовок"""
        print(Fore.GREEN + "=" * 60)
        print(Fore.GREEN + f"{text:^60}")
        print(Fore.GREEN + "=" * 60)

    def print_subheader(self, text):
        """Выводит подзаголовок"""
        print(Fore.YELLOW + f"\n{text}")
        print(Fore.YELLOW + "-" * 50)

    def get_country(self, mortar_name):
        """Определяет страну по названию миномета"""
        mortar_upper = mortar_name.upper()
        if "M252" in mortar_upper or "L16" in mortar_upper:
            return "[NATO]"
        elif "2B14" in mortar_upper or "2Б14" in mortar_upper or "2B11" in mortar_upper:
            return "[СССР]"
        elif "CHINESE" in mortar_upper or "TYPE" in mortar_upper:
            return "[Китай]"
        else:
            return ""

    def save_to_history(self, calculation):
        """Сохраняет расчет в историю"""
        calculation['timestamp'] = datetime.datetime.now().strftime("%H:%M:%S")
        self.history.append(calculation)
        
        # Ограничиваем историю последними 20 расчетами
        if len(self.history) > 20:
            self.history = self.history[-20:]

    def show_history(self):
        """Показывает историю расчетов с возможностью повторного использования"""
        if not self.history:
            print(Fore.YELLOW + "\nИстория расчетов пуста")
            input(Fore.CYAN + "Нажмите Enter для продолжения...")
            return None
            
        self.clear_screen()
        self.print_header("ИСТОРИЯ РАСЧЕТОВ")
        print(Fore.CYAN + "Выберите расчет для повторного использования или 0 для отмены:")
        
        for i, calc in enumerate(reversed(self.history), 1):
            print(Fore.WHITE + f"\n{i}. {calc['timestamp']} - {calc['mortar']} - {calc['shell']}")
            print(Fore.CYAN + f"   Дистанция: {calc['distance']}м | Высоты: {calc['mortar_alt']}м -> {calc['target_alt']}м")
            print(Fore.YELLOW + f"   Азимут: {calc.get('azimuth', '0')}")
            
            # Показываем результаты расчета
            if calc.get('results'):
                result = calc['results'][0]  # Берем первый результат
                print(Fore.GREEN + f"   Угол: {round(result['elevation'])}мил | Время: {result['time']:.1f}с")
        
        try:
            choice = int(input(Fore.CYAN + "\nВыберите номер расчета: "))
            if choice == 0:
                return None
            if 1 <= choice <= len(self.history):
                return self.history[-choice]  # Берем из конца списка
            else:
                print(Fore.RED + "Неверный выбор")
                return None
        except ValueError:
            print(Fore.RED + "Введите число")
            return None

    def show_help(self):
        """Показывает справку"""
        self.clear_screen()
        self.print_header("СПРАВКА ПО ПРОГРАММЕ")
        
        help_text = [
            ("История", "Можно повторно использовать предыдущие расчеты"),
            ("Быстрый ввод", "Нажмите Enter для значений по умолчанию"),
            ("Азимут", "Вводите в любом формате: 2-0, 1 5, 05 и т.д."),
            ("Высоты", "Учитывается разница высот между минометом и целью"),
            ("Повтор", "Из истории можно взять все параметры для нового расчета")
        ]
        
        for title, desc in help_text:
            print(Fore.YELLOW + f"\n{title}:")
            print(Fore.WHITE + f"  {desc}")
            
        input(Fore.CYAN + "\nНажмите Enter для продолжения...")

    def get_azimuth_input(self):
        """Запрос поправки по азимуту"""
        print(Fore.WHITE + "\nПоправка по азимуту (например: '2-0' или '1 5' или '0'):")
        azimuth = self.get_input("Введите поправку", input_type=str, default="0")
        return azimuth

    def perform_calculation(self, mortar_data, shell_data, target_dist, mortar_alt, target_alt):
        """Выполняет расчет и возвращает результаты"""
        results = []
        errors = []
        
        for ring_amount in shell_data:
            try:
                low_dist, high_dist, error_msg = self.find_closest_keys(shell_data[ring_amount]['Dists'], target_dist)
                
                if error_msg:
                    errors.append(f"{ring_amount} колец: {error_msg}")
                    continue
                
                if low_dist is None or high_dist is None:
                    errors.append(f"{ring_amount} колец: Дистанция вне диапазона")
                    continue
                
                dispersion = shell_data[ring_amount]['Dispersion']
                
                low_mils = shell_data[ring_amount]['Dists'][low_dist][0]
                high_mils = shell_data[ring_amount]['Dists'][high_dist][0]
                low_time = shell_data[ring_amount]['Dists'][low_dist][1]
                high_time = shell_data[ring_amount]['Dists'][high_dist][1]
                low_mils_per_100m = shell_data[ring_amount]['Dists'][low_dist][2]
                high_mils_per_100m = shell_data[ring_amount]['Dists'][high_dist][2]

                mils = self.interpolate(low_dist, high_dist, target_dist, low_mils, high_mils)
                time = self.interpolate(low_dist, high_dist, target_dist, low_time, high_time)
                mils_per_100m = self.interpolate(low_dist, high_dist, target_dist, low_mils_per_100m, high_mils_per_100m)
                
                # Поправка на высоту
                altitude_difference = mortar_alt - target_alt
                mils_per_1m = mils_per_100m / 100
                altitude_compensation = altitude_difference * mils_per_1m
                
                total_mils = mils + altitude_compensation
                
                result = {
                    'rings': ring_amount,
                    'elevation': total_mils,
                    'time': time,
                    'dispersion': dispersion,
                    'altitude_comp': altitude_compensation
                }
                
                results.append(result)
                
            except Exception as e:
                errors.append(f"{ring_amount} колец: Ошибка расчета")
                continue
        
        return results, errors

    def run_calculation(self, preset_data=None):
        """Основная функция расчета"""
        try:
            self.clear_screen()
            
            # Главный заголовок
            print(Fore.MAGENTA + "=" * 60)
            print(Fore.CYAN + "          КАЛЬКУЛЯТОР МИНОМЕТА v2.0")
            print(Fore.YELLOW + "        Артиллерийский помощник PRO")
            print(Fore.MAGENTA + "=" * 60)
            
            # Если есть preset данные, используем их
            if preset_data:
                selected_mortar = preset_data['mortar']
                selected_shell = preset_data['shell']
                preset_target_dist = preset_data['distance']
                preset_mortar_alt = preset_data['mortar_alt']
                preset_target_alt = preset_data['target_alt']
                preset_azimuth = preset_data.get('azimuth', '0')
                
                print(Fore.GREEN + f"\nИспользуются данные из истории:")
                print(Fore.WHITE + f"Миномет: {selected_mortar}")
                print(Fore.WHITE + f"Снаряд: {selected_shell}")
                print(Fore.WHITE + f"Дистанция: {preset_target_dist}м")
                print(Fore.WHITE + f"Высоты: {preset_mortar_alt}м -> {preset_target_alt}м")
                print(Fore.WHITE + f"Азимут: {preset_azimuth}")
                
                use_preset = self.get_input("\nИспользовать эти данные? (y/n)", input_type=str, default="y")
                if use_preset.lower() != 'y':
                    preset_data = None
            
            if not preset_data:
                print(Fore.CYAN + "\nВыберите действие:")
                print(Fore.WHITE + " 1. Новый расчет")
                print(Fore.WHITE + " 2. История расчетов")
                print(Fore.WHITE + " 3. Справка")
                print(Fore.RED + " 0. Выход")
                
                action = self.get_input("\nВаш выбор", input_type=int, min_val=0, max_val=3)
                
                if action == 0:
                    return False
                elif action == 2:
                    history_item = self.show_history()
                    if history_item:
                        return self.run_calculation(history_item)
                    else:
                        return True
                elif action == 3:
                    self.show_help()
                    return True
                
                # Выбор миномета
                mortar_keys = list(mortars.keys())
                self.print_subheader("Доступные минометы:")
                
                for i, x in enumerate(mortar_keys):
                    country = self.get_country(x)
                    print(Fore.WHITE + f'{i+1:2d}. {x} {country}')
                
                mortar_choice = self.get_input("\nВыберите номер миномета", input_type=int, min_val=1, max_val=len(mortar_keys))
                mortar_choice -= 1
                selected_mortar = mortar_keys[mortar_choice]
                mortar_data = mortars[selected_mortar]
                country = self.get_country(selected_mortar)
                
                self.clear_screen()
                self.print_header(f"ВЫБРАН: {selected_mortar} {country}")

                # Выбор снаряда
                shell_keys = list(mortar_data.keys())
                self.print_subheader("Доступные снаряды:")
                
                for i, x in enumerate(shell_keys):
                    print(Fore.WHITE + f'{i+1:2d}. {x}')
                
                shell_choice = self.get_input("\nВыберите номер снаряда", input_type=int, min_val=1, max_val=len(shell_keys)) - 1
                selected_shell = shell_keys[shell_choice]
                shell_data = mortar_data[selected_shell]
                
                self.clear_screen()
                self.print_header(f"{selected_mortar} {country} - {selected_shell}")

                # Ввод параметров стрельбы
                self.print_subheader("Основные параметры стрельбы")
                
                preset_target_dist = self.get_input("Дистанция до цели (м)", input_type=int, min_val=0, max_val=10000)
                preset_mortar_alt = self.get_input("Высота миномета (м)", input_type=int, default=0, min_val=-1000, max_val=10000)
                preset_target_alt = self.get_input("Высота цели (м)", input_type=int, default=0, min_val=-1000, max_val=10000)
                
                # Поправка по азимуту
                preset_azimuth = self.get_azimuth_input()
            else:
                # Используем preset данные
                mortar_data = mortars[selected_mortar]
                shell_data = mortar_data[selected_shell]
                country = self.get_country(selected_mortar)
            
            # Выполняем расчет
            results, errors = self.perform_calculation(mortar_data, shell_data, preset_target_dist, preset_mortar_alt, preset_target_alt)
            
            # Показываем результаты
            self.clear_screen()
            self.print_header("РЕЗУЛЬТАТЫ РАСЧЕТА")
            
            print(Fore.WHITE + f"Миномет: {selected_mortar} {country}")
            print(Fore.WHITE + f"Снаряд: {selected_shell}")
            print(Fore.WHITE + f"Дистанция: {preset_target_dist}м")
            print(Fore.WHITE + f"Высоты: {preset_mortar_alt}м -> {preset_target_alt}м")
            print(Fore.WHITE + f"Разница высот: {preset_mortar_alt - preset_target_alt}м")
            
            if preset_azimuth != "0":
                print(Fore.WHITE + f"Азимут: {preset_azimuth}")
            
            print(Fore.YELLOW + "\n" + "=" * 60)
            
            # Показываем ошибки если есть
            if errors:
                print(Fore.RED + "\nПроблемы с расчетом:")
                for error in errors:
                    print(Fore.RED + f"   {error}")
                print()
            
            if not results:
                print(Fore.RED + "Не удалось рассчитать ни одного варианта")
                print(Fore.YELLOW + "Попробуйте другую дистанцию или снаряд")
            else:
                # Сортируем результаты по количеству колец
                results.sort(key=lambda x: x['rings'])
                
                for result in results:
                    print(Fore.GREEN + f"\nКолец: {result['rings']}")
                    print(Fore.WHITE + f"   Разброс: {result['dispersion']}м")
                    print(Fore.CYAN + f"   Угол возвышения: {round(result['elevation'])} милов")
                    print(Fore.YELLOW + f"   Время полета: {round(result['time'], 2)} сек")
                    print(Fore.MAGENTA + f"   Поправка высоты: {round(result['altitude_comp'], 1)} милов")
            
            # Сохраняем в историю
            calculation_data = {
                'mortar': selected_mortar,
                'shell': selected_shell,
                'distance': preset_target_dist,
                'mortar_alt': preset_mortar_alt,
                'target_alt': preset_target_alt,
                'azimuth': preset_azimuth,
                'results': results
            }
            self.save_to_history(calculation_data)
            
            print(Fore.GREEN + "\n" + "=" * 60)
            print(Fore.CYAN + "Выберите действие:")
            print(Fore.WHITE + " 1. Новый расчет")
            print(Fore.WHITE + " 2. Использовать этот же расчет снова")
            print(Fore.WHITE + " 3. Главное меню")
            print(Fore.RED + " 0. Выход")
            
            next_action = self.get_input("\nВаш выбор", input_type=int, min_val=0, max_val=3)
            
            if next_action == 0:
                return False
            elif next_action == 1:
                return True
            elif next_action == 2:
                # Используем те же данные снова
                return self.run_calculation(calculation_data)
            else:
                return True
                
        except Exception as e:
            print(Fore.RED + f"\nОшибка: {str(e)}")
            input(Fore.YELLOW + "Нажмите Enter для продолжения...")
            return True

    def main(self):
        """Главная функция программы"""
        while True:
            try:
                if not self.run_calculation():
                    print(Fore.YELLOW + "\nДо свидания! Удачной стрельбы!")
                    break
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n\nПрограмма завершена пользователем")
                break

if __name__ == "__main__":
    # Проверяем зависимости
    try:
        import colorama
    except ImportError:
        print("Установите colorama: pip install colorama")
        exit()
    
    # Запускаем программу
    calculator = MortarCalculator()
    calculator.main()