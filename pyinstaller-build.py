#!/usr/bin/python3

import os
import re
import shutil
import codecs
import subprocess

SCRIPTS = ("opsi-admin", "opsi-backup")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

subprocess.check_call(["poetry", "install"])

for d in ("dist", "build"):
	if os.path.isdir(d):
		shutil.rmtree(d)

spec_a = ""
spec_m = []
spec_o = ""
for script in SCRIPTS:
	subprocess.check_call(["poetry", "run", "pyi-makespec", script])
	with codecs.open(f"{script}.spec", "r", "utf-8") as f:
		varname = script.replace("-", "_")
		data = f.read()
		data = re.sub(r"([\s\(])a\.", r"\g<1>" + varname + "_a.", data)
		#print(data)
		match = re.search(r"(.*)(a\s*=\s*)(Analysis[^\)]+\))(.*)", data, re.MULTILINE|re.DOTALL)
		if not spec_a:
			spec_a += match.group(1)
		spec_a += f"{varname}_a = {match.group(3)}\n"
		spec_o += match.group(4)
		spec_m.append(f"({varname}_a, '{script}', '{script}')")

with codecs.open(f"opsi-utils.spec", "w", "utf-8") as f:
	f.write(spec_a)
	f.write(f"\nMERGE( {', '.join(spec_m)} )\n")
	f.write(spec_o)

subprocess.check_call(["poetry", "run", "pyinstaller", "opsi-utils.spec"])


shutil.move(f"dist/{SCRIPTS[0]}", "dist/opsi-utils")
for script in SCRIPTS[1:]:
	shutil.move(f"dist/{script}/{script}", f"dist/opsi-utils/{script}")
	shutil.rmtree(f"dist/{script}")
