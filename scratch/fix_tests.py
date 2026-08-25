with open("tests/integration/test_slice_e2e.py", "r") as f:
    content = f.read()

content = content.replace('"What is the exit load?"', '"What is the exit load for HDFC Mid Cap?"')
content = content.replace(
    '"What is the investment objective?"',
    '"What is the investment objective for HDFC Mid Cap?"',
)

with open("tests/integration/test_slice_e2e.py", "w") as f:
    f.write(content)
