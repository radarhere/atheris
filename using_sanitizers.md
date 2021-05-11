# Using Sanitizers with Atheris and Native Extensions

When fuzzing native extensions, we strongly recommend that Clang sanitizers be
used. Atheris supports Address Sanitizer (`-fsanitize=address`) and Undefined Behavior Sanitizer (`-fsanitize=undefined`).

## Step 1: Compiling your Extension

Usually, you can compile a sanitized extension like this:

```
CC="/usr/bin/clang" CFLAGS="-fsanitize=address,fuzzer-no-link" CXX="/usr/bin/clang++" CXXFLAGS="-fsanitize=address,fuzzer-no-link" pip install .
```

If your extension is too complex and this doesn't work, you may have to make specific changes to its build system.

## Step 2: Use an external libFuzzer

For technical reasons detailed below, libFuzzer must not be linked into Atheris if sanitizers are being used. First, replace this:

```
import atheris
```

With this:

```
import atheris_no_libfuzzer as atheris
```

Now that libFuzzer is no longer being provided by Atheris, it needs to be provided elsewhere. There are two options:

### Option A: Sanitizer+libFuzzer preloads

If you can use this option, we recommend it; it is significantly easier than option #2. (However, this option is not yet supported on Mac). When Atheris is installed, it attempts to generate custom ASan and UBSan shared libraries that have libFuzzer linked in. You can find these libraries in the directory returned by this command:

```
python -c "import atheris; import os; print(os.path.dirname(atheris.path()))"
```

These files will be called:
 - `asan_with_fuzzer.so`
 - `ubsan_with_fuzzer.so`
 - `ubsan_cxx_with_fuzzer.so`

If these files are present, it means Atheris succesfully generated the files at installation time, and you can use this option. Simply `LD_PRELOAD` the right `.so` file, and you're good to go. Here's a complete example:

```
LD_PRELOAD="$(python -c "import atheris; import os; print(os.path.dirname(atheris.path()))")/asan_with_fuzzer.so" python ./my_fuzzer.py
```

### Option 2: Linking libFuzzer into Python

This option doesn't rely on these custom shared libraries; instead, it involves building a modified CPython. We provide a script and patch file that attempts to do this
for Python 3.8.6 in the `third_party` directory.

```
cd third_party
./build_modified_libfuzzer.sh
```

This will clone CPython, check out version 3.8.6, apply the patch file, find
libFuzzer, and build. It will not install; you can either `make install` or just
use `./python` directly from that directory.

If your new Python is missing certain libraries, you may need to install some
prerequisites using `apt install` (or your platform's equivalent). See regular
Python build documentation for help.

We provide a patch file for CPython 3.8.6. Other nearby versions can likely be
patched in a similar manner.

If you have issues building a modified CPython, or wish to provide patches for
other versions, please open an issue or provide a PR.

Once libFuzzer is linked into Python, you can `LD_PRELOAD` a normal sanitizer, rather than having to LD_PRELOAD a special one generated by Atheris. You can generally find this sanitizer by running `clang -print-search-dirs` and looking in the descendants of the first "libraries" dir.

#### The correct libFuzzer

Atheris requires a recent version of libFuzzer, but for most reasonable
versions, it can perform an in-place upgrade. The correct version (upgraded if
needed) is written to the `site-packages` directory adjacent to where Atheris
is installed. You can find it in the directory returned by this command:

```
python3 -c "import atheris; import os; print(os.path.dirname(atheris.path()))"
```

The `build_modified_libfuzzer.sh` script uses the libFuzzer found there by
default.

## Leak detection

Python is known to leak certain data, such as at interpreter initialization time. You should disable leak detection, for example with `-detect_leaks=0`.

## Why this is necessary

Certain code coverage symbols exported by libFuzzer are also exported by ASan
and UBSan. Normally, this isn't a problem, because ASan/UBSan export them
as weak symbols - libFuzzer's symbols take precedence. However, when ASan/UBSan
are preloaded and libFuzzer is loaded as part of a shared library (Atheris),
the weak symbols are loaded first. This causes code coverage information to be
sent to ASan/UBSan, not libFuzzer.

By linking libFuzzer into Python directly, or by linking libFuzzer into ASan/UBSan,
the dynamic linker can correctly select the strong symbols from libFuzzer rather
than the weak symbols from ASan/UBSan.

## What if I'm not using a Sanitizer?

While we recommend that you use a sanitizer when fuzzing native code, it's not mandatory. If you'd like to use Atheris to fuzz native code without a sanitizer, you should still build your extension with `-fsanitize=fuzzer-no-link`, and then `LD_PRELOAD` *the atheris shared library* itself.

```
LD_PRELOAD="path/to/atheris.so" python ./your_fuzzer.py
```

If you want to make a Python fuzzer that runs both with or without a sanitizer, you can use this code pattern:

```
try:
  import atheris_no_libfuzzer as atheris
except ImportError:
  import atheris
```

Loading `atheris_no_libfuzzer` will fail if libFuzzer hasn't been linked into CPython and hasn't been preloaded.