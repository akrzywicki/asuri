import os
import re

def generate_readme():
    articles_dir = "rassylki"
    readme_path = "README.md"
    
    # Read all files
    files = [f for f in os.listdir(articles_dir) if f.endswith('.md')]
    files.sort()
    
    # Generate content
    content = """# Энергетика Взаимоотношений (asuri.ru)

Сборник статей сайта asuri.ru.

**О чем эти статьи?**
Эти статьи представляют собой практическую психологию и социальную философию, упакованные в эзотерическую терминологию. Автор использует понятия вроде эгрегоров, энергообмена и нейронных связей как функциональные модели для объяснения поведения людей. В текстах много здравого смысла, логики и точных наблюдений за бытовыми ситуациями, отношениями и механизмами мотивации. Эзотерический язык служит здесь инструментом для структурирования сложных психологических процессов.

Воспринимайте эти материалы как альтернативный аналитический взгляд на человеческие взаимоотношения.

## Оглавление

"""
    
    for filename in files:
        # Extract title from filename (remove number prefix and .md)
        title = filename.split('_', 1)[1][:-3].replace('-', ' ')
        filepath = f"{articles_dir}/{filename}"
        content += f"- [{title}]({filepath})\n"
        
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"README.md generated with {len(files)} links.")

if __name__ == "__main__":
    generate_readme()