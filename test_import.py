try:
    exec(open('shared/interfaces/mandala_system.py').read())
    print('Success')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()