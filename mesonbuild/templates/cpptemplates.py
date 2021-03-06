# Copyright 2019 The Meson development team

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re


hello_cpp_template = '''#include <iostream>

#define PROJECT_NAME "{project_name}"

int main(int argc, char **argv) {{
    if(argc != 1) {{
        std::cout << argv[0] <<  "takes no arguments.\\n";
        return 1;
    }}
    std::cout << "This is project " << PROJECT_NAME << ".\\n";
    return 0;
}}
'''

hello_cpp_meson_template = '''project('{project_name}', 'cpp',
  version : '{version}',
  default_options : ['warning_level=3',
                     'cpp_std=c++14'])

exe = executable('{exe_name}', '{source_name}',
  install : true)

test('basic', exe)
'''

lib_hpp_template = '''#pragma once
#if defined _WIN32 || defined __CYGWIN__
  #ifdef BUILDING_{utoken}
    #define {utoken}_PUBLIC __declspec(dllexport)
  #else
    #define {utoken}_PUBLIC __declspec(dllimport)
  #endif
#else
  #ifdef BUILDING_{utoken}
      #define {utoken}_PUBLIC __attribute__ ((visibility ("default")))
  #else
      #define {utoken}_PUBLIC
  #endif
#endif

namespace {namespace} {{

class {utoken}_PUBLIC {class_name} {{

public:
  {class_name}();
  int get_number() const;

private:

  int number;

}};

}}

'''

lib_cpp_template = '''#include <{header_file}>

namespace {namespace} {{

{class_name}::{class_name}() {{
    number = 6;
}}

int {class_name}::get_number() const {{
  return number;
}}

}}
'''

lib_cpp_test_template = '''#include <{header_file}>
#include <iostream>

int main(int argc, char **argv) {{
    if(argc != 1) {{
        std::cout << argv[0] << " takes no arguments.\\n";
        return 1;
    }}
    {namespace}::{class_name} c;
    return c.get_number() != 6;
}}
'''

lib_cpp_meson_template = '''project('{project_name}', 'cpp',
  version : '{version}',
  default_options : ['warning_level=3', 'cpp_std=c++14'])

# These arguments are only used to build the shared library
# not the executables that use the library.
lib_args = ['-DBUILDING_{utoken}']

shlib = shared_library('{lib_name}', '{source_file}',
  install : true,
  cpp_args : lib_args,
  gnu_symbol_visibility : 'hidden',
)

test_exe = executable('{test_exe_name}', '{test_source_file}',
  link_with : shlib)
test('{test_name}', test_exe)

# Make this library usable as a Meson subproject.
{ltoken}_dep = declare_dependency(
  include_directories: include_directories('.'),
  link_with : shlib)

# Make this library usable from the system's
# package manager.
install_headers('{header_file}', subdir : '{header_dir}')

pkg_mod = import('pkgconfig')
pkg_mod.generate(
  name : '{project_name}',
  filebase : '{ltoken}',
  description : 'Meson sample project.',
  subdirs : '{header_dir}',
  libraries : shlib,
  version : '{version}',
)
'''


def create_exe_cpp_sample(project_name, project_version):
    lowercase_token = re.sub(r'[^a-z0-9]', '_', project_name.lower())
    source_name = lowercase_token + '.cpp'
    open(source_name, 'w').write(hello_cpp_template.format(project_name=project_name))
    open('meson.build', 'w').write(hello_cpp_meson_template.format(project_name=project_name,
                                                                   exe_name=lowercase_token,
                                                                   source_name=source_name,
                                                                   version=project_version))


def create_lib_cpp_sample(project_name, version):
    lowercase_token = re.sub(r'[^a-z0-9]', '_', project_name.lower())
    uppercase_token = lowercase_token.upper()
    class_name = uppercase_token[0] + lowercase_token[1:]
    test_exe_name = lowercase_token + '_test'
    namespace = lowercase_token
    lib_hpp_name = lowercase_token + '.hpp'
    lib_cpp_name = lowercase_token + '.cpp'
    test_cpp_name = lowercase_token + '_test.cpp'
    kwargs = {'utoken': uppercase_token,
              'ltoken': lowercase_token,
              'header_dir': lowercase_token,
              'class_name': class_name,
              'namespace': namespace,
              'header_file': lib_hpp_name,
              'source_file': lib_cpp_name,
              'test_source_file': test_cpp_name,
              'test_exe_name': test_exe_name,
              'project_name': project_name,
              'lib_name': lowercase_token,
              'test_name': lowercase_token,
              'version': version,
              }
    open(lib_hpp_name, 'w').write(lib_hpp_template.format(**kwargs))
    open(lib_cpp_name, 'w').write(lib_cpp_template.format(**kwargs))
    open(test_cpp_name, 'w').write(lib_cpp_test_template.format(**kwargs))
    open('meson.build', 'w').write(lib_cpp_meson_template.format(**kwargs))
