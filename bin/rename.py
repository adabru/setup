#!/usr/bin/env python

#print("rename")
#
#

#files = readdir('.')
#preview(files, "")
#def oninput(regex):
#  if input is <enter>:
#    apply()
#    exit()
#  elif input is <esc>:
#    exit()
#  else:
#    preview(files, regex)
#def preview(files, regex):
# for f in files:
#   print(f + " → " + regex.exec(f))
# print("press <enter> to apply or <esc> to cancel")
#def apply(files, regex):
#  for f in files:
#    os.rename(f, regex.exec(f))

# rename = s => {
#   [,r,n] = s.split(s[0])
#   r = new RegExp(r)
#   _old = fs.readdirSync('.').filter(f => r.test(f))
#   _new = _old.map(f => {
#     m = r.exec(f)
#     return n.replace(/\$([0-9])/g, ([,i]) => m[i])
#   })
#   for(i in _old) console.log(`${_old[i]}  →  ${_new[i]}`)
#   console.log('Ok? (enter _() if yes)')
#   return () => _old.forEach((_,i) => fs.renameSync(_old[i], _new[i]))
# }