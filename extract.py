def extract(text: str, prefix: str, suffix: str):
    start = text.index(prefix) + len(prefix)
    end = text.index(suffix, start)
    return text[start:end]


code = open('glcorearb.h').read()
code = code.replace('GLAPI', '').replace('APIENTRY', '').replace('const', '').replace('(void)', '()')


def get_constants(version: str):
    chunk = extract(code, f'#ifndef {version}', f'#endif /* {version} */')
    constants = [x for x in chunk.split('\n') if x.startswith('#define')]

    for line in constants:
        name, value = line.split()[1:]
        value = value.removesuffix('u').removesuffix('ull')
        if name != version:
            yield name, value


def get_functions(version: str):
    chunk = extract(code, f'#ifndef {version}', f'#endif /* {version} */')
    functions = extract(chunk, '#ifdef GL_GLEXT_PROTOTYPES', '#endif')
    functions = [x for x in functions.split('\n') if x.strip()]

    for line in functions:
        name = line.split('(')[0].split()[-1]
        res = line.split('(')[0].replace(name, '').strip()
        args = [x.strip() for x in extract(line, '(', ')').split(',') if x]
        args = ['void *' if '*' in x else x.rsplit(' ', 1)[0] for x in args]
        yield name, res, args


versions = [
    'GL_VERSION_1_0',
    'GL_VERSION_1_1',
    'GL_VERSION_1_2',
    'GL_VERSION_1_3',
    'GL_VERSION_1_4',
    'GL_VERSION_1_5',
    'GL_VERSION_2_0',
    'GL_VERSION_2_1',
    'GL_VERSION_3_0',
    'GL_VERSION_3_1',
    'GL_VERSION_3_2',
    'GL_VERSION_3_3',
    'GL_VERSION_4_0',
    'GL_VERSION_4_1',
    'GL_VERSION_4_2',
    'GL_VERSION_4_3',
    'GL_VERSION_4_4',
    'GL_VERSION_4_5',
    'GL_VERSION_4_6',
]

gltypes = {
    'GLbitfield': 'c_int',
    'GLsizeiptr': 'c_ssize_t',
    'GLuint64': 'c_longlong',
    'void *': 'c_void_p',
    'GLboolean': 'c_int',
    'GLshort': 'c_short',
    'GLenum': 'c_int',
    'GLint': 'c_int',
    'GLDEBUGPROC': 'c_void_p',
    'void': 'None',
    'GLdouble': 'c_double',
    'GLintptr': 'c_ssize_t',
    'GLsync': 'c_void_p',
    'GLubyte': 'c_byte',
    'GLuint': 'c_int',
    'GLsizei': 'c_int',
    'GLfloat': 'c_float',
    'GLubyte *': 'c_char_p',
}


print('from ctypes import CFUNCTYPE, c_byte, c_char_p, c_double, c_float, c_int, c_longlong, c_short, c_ssize_t, c_void_p, cast\n\n')
print('class OpenGL:')

for version in versions:
    for name, value in get_constants(version):
        print(f'    {name} = {value}')

print()
print('    def __init__(self, loader):')
print('        def load(name, *args):')
print('            return cast(loader.load_opengl_function(name), CFUNCTYPE(*args))')
print()

for version in versions:
    for name, res, args in get_functions(version):
        args = ', '.join([gltypes[res]] + [gltypes[x] for x in args])
        print(f'        self.{name} = load(\'{name}\', {args})')
