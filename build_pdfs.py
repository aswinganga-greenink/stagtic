import json
import os
import subprocess
import shutil
import re

def escape_latex(text):
    if not isinstance(text, str):
        text = str(text)
    
    chars_to_escape = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}'
    }
    
    res = ""
    for c in text:
        res += chars_to_escape.get(c, c)
            
    res = res.replace('<=', r'$\le$')
    res = res.replace('>=', r'$\ge$')
    res = res.replace('<', r'$<$')
    res = res.replace('>', r'$>$')
    res = res.replace('\n', ' \\\\ \n')
    return res

def generate_latex(q):
    title = escape_latex(q['title'])
    difficulty = escape_latex(q['difficulty'])
    statement = escape_latex(q['statement'])
    i_format = escape_latex(q['input_format'])
    o_format = escape_latex(q['output_format'])
    
    constraints_latex = "\\begin{itemize}[leftmargin=*]\n"
    for c in q['constraints']:
        constraints_latex += f"\\item {escape_latex(c)}\n"
    constraints_latex += "\\end{itemize}"
    
    test_cases_latex = ""
    for idx, tc in enumerate(q['test_cases']):
        tc_in = escape_latex(tc['input'])
        tc_out = escape_latex(tc['output'])
        tc_exp = escape_latex(tc['explanation'])
        test_cases_latex += f"""
\\begin{{testcasebox}}{{Test Case {idx+1}}}
\\textbf{{Input:}} \\\\
\\texttt{{{tc_in}}} \\\\[0.2cm]
\\textbf{{Output:}} \\\\
\\texttt{{{tc_out}}} \\\\[0.2cm]
\\textbf{{Explanation:}} \\\\
{tc_exp}
\\end{{testcasebox}}
\\vspace{{0.2cm}}
"""

    return f"""\\documentclass[12pt, a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in, top=1.2in, bottom=1.2in}}
\\usepackage{{helvet}}
\\renewcommand{{\\familydefault}}{{\\sfdefault}}
\\usepackage{{xcolor}}
\\usepackage{{tcolorbox}}
\\tcbuselibrary{{skins, breakable}}
\\usepackage{{fancyhdr}}
\\usepackage{{enumitem}}

\\definecolor{{primary}}{{HTML}}{{2B3A42}}
\\definecolor{{secondary}}{{HTML}}{{3F5765}}
\\definecolor{{accent}}{{HTML}}{{FF530D}}
\\definecolor{{bglight}}{{HTML}}{{F0F4F8}}
\\definecolor{{boxborder}}{{HTML}}{{BDC3C7}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{\\textbf{{\\textcolor{{primary}}{{Stagtic Coding Competition}}}}}}
\\fancyhead[R]{{\\textbf{{\\textcolor{{secondary}}{{{difficulty} Round}}}}}}
\\renewcommand{{\\headrulewidth}}{{1pt}}
\\renewcommand{{\\headrule}}{{\\hbox to\\headwidth{{\\color{{primary}}\\leaders\\hrule height \\headrulewidth\\hfill}}}}
\\fancyfoot[C]{{\\thepage}}

\\newtcolorbox{{sectionbox}}[1]{{
    colback=bglight,
    colframe=primary,
    coltitle=white,
    title=\\textbf{{#1}},
    arc=3mm,
    boxrule=1pt,
    fonttitle=\\large,
    breakable,
    left=4mm, right=4mm, top=3mm, bottom=3mm,
    drop shadow=black!10!white
}}

\\newtcolorbox{{testcasebox}}[1]{{
    colback=white,
    colframe=boxborder,
    coltitle=secondary,
    title=\\textbf{{#1}},
    arc=2mm,
    boxrule=0.5pt,
    fonttitle=\\normalsize,
    titlerule=0.5pt,
    toptitle=1.5mm, bottomtitle=1.5mm,
    colbacktitle=bglight,
    breakable,
    left=3mm, right=3mm, top=2mm, bottom=2mm
}}

\\begin{{document}}

\\begin{{center}}
    {{\\Huge \\textbf{{\\textcolor{{primary}}{{{title}}}}}}} \\\\[0.4cm]
    {{\\large \\textbf{{Difficulty:}} \\textcolor{{accent}}{{{difficulty}}}}} \\\\[0.6cm]
\\end{{center}}

\\begin{{sectionbox}}{{Problem Statement}}
{statement}
\\end{{sectionbox}}

\\vspace{{0.2cm}}

\\begin{{sectionbox}}{{Input \\& Output Format}}
\\textbf{{Input:}} \\\\
{i_format} \\\\[0.3cm]
\\textbf{{Output:}} \\\\
{o_format}
\\end{{sectionbox}}

\\vspace{{0.2cm}}

\\begin{{sectionbox}}{{Constraints}}
{constraints_latex}
\\end{{sectionbox}}

\\vspace{{0.5cm}}
{{\\Large \\textbf{{\\textcolor{{primary}}{{Test Cases}}}}}}
\\vspace{{0.3cm}}

{test_cases_latex}

\\end{{document}}
"""

def process_file(json_file):
    with open(json_file, 'r') as f:
        questions = json.load(f)
    
    for q in questions:
        section = q['section'].lower().strip()
        title = q['title'].strip()
        dir_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', title).lower()
        
        target_dir = os.path.join(os.getcwd(), section, dir_name)
        os.makedirs(target_dir, exist_ok=True)
        
        tex_path = os.path.join(target_dir, 'problem.tex')
        pdf_path = os.path.join(target_dir, 'problem.pdf')
        
        latex_content = generate_latex(q)
        
        with open(tex_path, 'w') as f:
            f.write(latex_content)
            
        print(f"Compiling PDF for {title}...")
        subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', 'problem.tex'], 
            cwd=target_dir, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        for ext in ['.aux', '.log', '.tex']:
            file_to_remove = os.path.join(target_dir, f"problem{ext}")
            if os.path.exists(file_to_remove):
                os.remove(file_to_remove)

if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:]:
        process_file(arg)
