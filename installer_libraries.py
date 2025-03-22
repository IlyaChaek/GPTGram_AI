import subprocess
import time
import pkg_resources
import os

os.system('cls' if os.name == 'nt' else 'clear')
subprocess.run(["installer_fonts.bat"], shell=True)
time.sleep(10)
os.system('cls' if os.name == 'nt' else 'clear')
print('---------------------')
print('Установка библиотек займет какое-то время (в зависимости от скорости интернета и процессора), пожалуйста, подождите...')
print('---------------------')

time.sleep(5)

def install_all_packages():
    try:
        with open('requirements.txt', 'r') as file:
            packages = [line.strip() for line in file if line.strip() and not line.startswith('#')]
            print('Устанавливаю все зависимости...')
            subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])
        print('\nВсе зависимости установлены')
    except FileNotFoundError:
        print('Файл requirements.txt не найден')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка при установке пакетов: {e}')

def install_missing_packages():
    try:
        with open('requirements.txt', 'r') as file:
            packages = [line.strip() for line in file if line.strip() and not line.startswith('#')]

        installed_packages = {pkg.key for pkg in pkg_resources.working_set}

        for package in packages:
            package_name = package.split('==')[0].lower() if '==' in package else package.lower()
            if package_name in installed_packages:
                print(f'Пакет {package} уже установлен, пропускаю.')
            else:
                print(f'Устанавливаю {package}...')
                subprocess.check_call(['pip', 'install', package])

        print('\nВсе зависимости установлены')
    except FileNotFoundError:
        print('Файл requirements.txt не найден')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка при установке пакета: {e}')

if __name__ == '__main__':
    print('Выберите режим:')
    print('1 - Проверять и устанавливать только отсутствующие библиотеки (Рекомендовано)')
    print('2 - Установить все зависимости без проверки (Альтернативный вариант)')
    choice = input('Ваш выбор (1 или 2): ').strip()

    print('\nОбновляю pip до последней версии...')
    subprocess.check_call(['python', '-m', 'pip', 'install', '--upgrade', 'pip'])
    print('pip успешно обновлён\n')

    if choice == '1':
        install_missing_packages()
    elif choice == '2':
        install_all_packages()
    else:
        print('Неверный выбор. Завершаю работу.')
os.system('cls' if os.name == 'nt' else 'clear')