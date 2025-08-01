try:
    exec(open('main.py').read())
    print('ContentModerationEngine' in globals())
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()