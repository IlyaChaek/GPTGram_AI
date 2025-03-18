import subprocess
def install_requirements():
    try:
        with open('requirements.txt', 'r') as file:
            packages = file.read().splitlines()
            for package in packages:
                if package.strip() and not package.startswith('#'):
                    print(f'Устанавливаю {package}...')
                    subprocess.check_call(['pip', 'install', package])
        print('Все зависимости установлены')
    except FileNotFoundError:
        print('Файл requirements.txt не найден')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка при установке пакета: {e}')
if __name__ == '__main__':
    install_requirements()