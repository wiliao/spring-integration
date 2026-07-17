with open(r"C:\Samples-03-spring-integration-camel\spring-integration\docs\Enterprise Integration Patterns - Designing, Building And Deploying Messaging Solutions.md", 'r', encoding='utf-8') as f:
    content = f.read()

print('Count of "such as: - ":', content.count('such as: - '))
print('Count of ":\\n- ":', content.count(':\n- '))
print('Count of ": - ":', content.count(': - '))
print('Count of "\\n- ":', content.count('\n- '))
print('Total length:', len(content))
print('Total lines:', content.count('\n'))
# Show the area around the test
idx = content.find('Who Should Read')
print('---')
print(content[idx:idx+800])
print('---')
idx = content.find('All integration solutions have to deal')
print(content[idx:idx+1500])
