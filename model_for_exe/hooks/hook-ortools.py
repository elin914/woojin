from PyInstaller.utils.hooks import collect_data_files

# ortools 패키지 안의 모든 데이터 파일과 DLL을 재귀적으로 수집
datas = collect_data_files('ortools')