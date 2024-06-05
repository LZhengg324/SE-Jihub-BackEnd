description = "hello my friend"
labels = ["apple", "banana", "cherry"]
ss = ""
for i, label in enumerate(labels):
    ss = ss + label
    if (i < len(labels) - 1):
        ss += ";&;"
ss = ss + "#@#" + description

print(ss)

labels_tmp, description = ss.split("#@#")
labels = labels_tmp.split(";&;")
print(labels)
print(description)