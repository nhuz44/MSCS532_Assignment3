"""Regenerate the chart from local CSV measurements.
"""
from __future__ import annotations
import csv
from datetime import date
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent


def read_csv(filename: str) -> list[dict]:
    with (ROOT / filename).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def chart_sorting(records: list[dict]) -> None:
    plt.rcParams.update({'font.size': 9})
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.45), dpi=170)
    for ax, distributions in zip(axes,
          [('Sorted', 'Reverse sorted'), ('Random', 'Repeated values')]):
        for name in distributions:
            for algo, line in [('Randomized Quicksort', '-'), ('First-pivot Quicksort', '--')]:
                selected = sorted((r for r in records if r['dataset'] == name and r['algorithm'] == algo), key=lambda x:int(x['n']))
                ax.plot([int(r['n']) for r in selected], [float(r['median_time_ms']) for r in selected],
                        linestyle=line, marker='o', linewidth=1.7,
                        label=f'{name}: {"Random" if algo.startswith("Randomized") else "First"}')
        ax.set_xlabel('Input size (elements)')
        ax.set_ylabel('Median execution time (ms)')
        ax.set_title('Ordered inputs' if distributions[0] == 'Sorted' else 'Random and duplicate-heavy inputs')
        ax.grid(alpha=.23)
        ax.legend(fontsize=7, loc='upper left')
    fig.tight_layout(pad=1.35)
    fig.savefig(ROOT / 'quicksort_comparison.png', bbox_inches='tight')
    plt.close(fig)


def setup_style(doc):
    s = doc.styles['Normal']
    s.font.name = 'Times New Roman'
    s.font.size = Pt(12)
    s.paragraph_format.line_spacing = 2
    s.paragraph_format.space_after = Pt(0)
    for h in ('Title', 'Heading 1', 'Heading 2'):
        st = doc.styles[h]
        st.font.name = 'Times New Roman'
        st.font.color.rgb = RGBColor(0,0,0)
        st.font.bold = True
        st.paragraph_format.line_spacing = 2
        st.paragraph_format.space_before = Pt(0)
        st.paragraph_format.space_after = Pt(0)
    sec = doc.sections[0]
    sec.top_margin = sec.bottom_margin = Inches(1)
    sec.left_margin = sec.right_margin = Inches(1)
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer.paragraph_format.line_spacing = 1
    footer.add_run('')
    field = OxmlElement('w:fldSimple')
    field.set(qn('w:instr'), 'PAGE')
    footer._p.append(field)
    doc.core_properties.author = 'Nhuja Shakya'
    doc.core_properties.title = 'Assignment 3: Understanding Algorithm Efficiency and Scalability'


def para(doc, text='', bold_lead=None):
    p=doc.add_paragraph(style='Normal')
    if bold_lead and text.startswith(bold_lead):
        p.add_run(bold_lead).bold=True
        p.add_run(text[len(bold_lead):])
    else:
        p.add_run(text)
    return p


def heading(doc, text, level=1):
    p=doc.add_paragraph(style='Heading 1' if level==1 else 'Heading 2')
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER if level==1 else WD_ALIGN_PARAGRAPH.LEFT
    p.add_run(text)
    return p


def table(doc, headers, rows, widths=None):
    t=doc.add_table(rows=1, cols=len(headers))
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.autofit=False
    for i, h in enumerate(headers):
        cell=t.rows[0].cells[i]
        cell.text=str(h)
        cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    for row in rows:
        cells=t.add_row().cells
        for i,entry in enumerate(row):
            cells[i].text=str(entry)
            cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    for n,row in enumerate(t.rows):
        for i,c in enumerate(row.cells):
            if widths:
                c.width= Inches(widths[i])
            for p in c.paragraphs:
                p.paragraph_format.line_spacing=1
                p.paragraph_format.space_before=Pt(1)
                p.paragraph_format.space_after=Pt(1)
                p.alignment= WD_ALIGN_PARAGRAPH.LEFT if i==0 else WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.size=Pt(9)
                    if n==0:run.font.bold=True
            tcPr=c._tc.get_or_add_tcPr()
            borders=tcPr.first_child_found_in('w:tcBorders')
            if borders is None:
                borders=OxmlElement('w:tcBorders');tcPr.append(borders)
            for edge in ('top','left','bottom','right','insideH','insideV'):
                el=borders.find(qn('w:'+edge))
                if el is None: el=OxmlElement('w:'+edge);borders.append(el)
                el.set(qn('w:val'),'single')
                el.set(qn('w:color'),'555555')
                el.set(qn('w:sz'),'7')
    return t


def caption(doc, text):
    p=doc.add_paragraph()
    p.paragraph_format.line_spacing=1
    p.paragraph_format.space_before=Pt(5)
    p.paragraph_format.space_after=Pt(4)
    r=p.add_run(text)
    r.font.size=Pt(10)
    return p


def new_page(doc):
    doc.add_page_break()


def generate():
    records=read_csv('benchmark_results.csv')
    hashes=read_csv('hash_load_results.csv')
    chart_sorting(records)
    env=(ROOT/'environment.txt').read_text(encoding='utf-8')
    platform_line=next((s.removeprefix('Platform: ') for s in env.splitlines() if s.startswith('Platform: ')), 'not reported')
    python_line=next((s.removeprefix('Python: ') for s in env.splitlines() if s.startswith('Python: ')), 'not reported')
    look={(r['dataset'],int(r['n']),r['algorithm']):float(r['median_time_ms']) for r in records}
    largest=max(int(r['n']) for r in records)
    doc=Document(); setup_style(doc)
    # Student APA title page.
    for _ in range(3):doc.add_paragraph('')
    for line in ['Assignment 3: Understanding Algorithm Efficiency and Scalability',
                 'Randomized Quicksort and Hashing with Chaining',
                 'Nhuja Shakya',
                 'University of the Cumberlands',
                 'MSCS-532-B01: Algorithms and Data Structures',
                 'November 9, 2026']:
        p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        rr=p.add_run(line)
        if line.startswith('Assignment 3:'):rr.bold=True
    new_page(doc)
    heading(doc,'Assignment 3: Algorithm Efficiency and Scalability')
    heading(doc,'Purpose and Implementation',2)
    para(doc,'This assignment compares randomized Quicksort with a deterministic first-element-pivot version and implements a separate-chaining hash table. Both sorting variants use the same iterative, three-way in-place partitioner; only pivot selection changes. The randomized method chooses an integer position uniformly from the active subarray. Three-way partitioning places duplicate pivot values into one completed middle region, so equal values do not repeatedly enter new partitions (Bentley & McIlroy, 1993). Both methods return an ascending sorted copy of the input; an explicit stack avoids Python recursion-limit failures.')
    heading(doc,'Randomized Quicksort: Expected Complexity',2)
    para(doc,'For n distinct keys, partitioning takes Θ(n) work. If the random pivot has rank k + 1, the subproblems contain k and n − 1 − k elements. Thus the expected-time recurrence is E[T(n)] = (1/n) Σₖ₌₀ⁿ⁻¹(E[T(k)] + E[T(n − 1 − k)]) + cn. It resolves to Θ(n log n); randomization removes dependence on the original input order for the expected bound, not the possibility of an unlucky Θ(n²) execution (Sedgewick, 1978).')
    para(doc,'An indicator-variable proof makes the bound precise. Rank the distinct keys x₁ < ··· < xₙ and let Xᵢⱼ equal 1 when ranks i and j are directly compared, or 0 otherwise. The two ranks meet only when the first pivot from the rank interval [i, j] is one of its endpoints. Therefore P(Xᵢⱼ = 1) = 2/(j − i + 1). By linearity of expectation, E[C] = Σᵢ<ⱼ E[Xᵢⱼ] = Σᵢ<ⱼ 2/(j − i + 1) ≤ 2nHₙ = O(n log n). The comparison-sorting lower bound supplies Ω(n log n) for distinct keys. Our three-way partitioner may perform up to two comparisons per visited element, preserving this asymptotic expected bound, while duplicate keys are removed together.')
    heading(doc,'Experiment Design',2)
    para(doc,f'Four input distributions—random, already sorted, reverse sorted, and repeated values from eight distinct keys—were tested at sizes 250, 750, 1,500, and {largest:,}. Each algorithm sorted the same input values, and the median wall-clock time was recorded over seven trials per configuration using Python perf_counter_ns. Random inputs were generated using fixed seeds, while randomized pivots used different seeds on successive trials. Results were validated against Python sorted() before being recorded. The recorded environment was {platform_line}, Python {python_line}. Times are environment-specific, not hardware-independent performance guarantees.')
    heading(doc,'Empirical Quicksort Results')
    caption(doc,f'Table 1. Median execution time at n = {largest:,} (milliseconds; seven trials)')
    table_rows=[]
    for kind in ('Random','Sorted','Reverse sorted','Repeated values'):
        table_rows.append((kind, f'{look[(kind,largest,"Randomized Quicksort")]:.4f}',f'{look[(kind,largest,"First-pivot Quicksort")]:.4f}'))
    table(doc,['Input distribution','Randomized','First-element pivot'],table_rows,[2.6,1.75,2.15])
    caption(doc,'Figure 1. Median sorting time by input distribution and array length (from benchmark_results.csv).')
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.line_spacing=1
    p.add_run().add_picture(str(ROOT/'quicksort_comparison.png'),width=Inches(6.35))
    heading(doc,'Interpretation',2)
    a=look[('Reverse sorted',largest,'First-pivot Quicksort')]
    b=look[('Reverse sorted',largest,'Randomized Quicksort')]
    para(doc,f'At {largest:,} elements, reverse-sorted input took {a:.4f} ms with a first-element pivot, versus {b:.4f} ms with randomized pivots (about {a/b:.1f} times longer). Ordered inputs expose poor deterministic partitions; the three-way swapping pattern also affects the exact size of that penalty. With random data, the methods were closer and the deterministic variant could win by avoiding random-number generation. With repeated values, both benefited from grouping equal keys into a single partition. Real timings reflect interpreter overhead, memory access, and particular pivot samples; small differences are not proof of a universal advantage.')
    heading(doc,'Hashing with Separate Chaining')
    heading(doc,'Implementation and Hash Function',2)
    para(doc,'The ChainedHashTable class stores a list of (integer key, value) pairs in each bucket. It supports insert, search, and delete, including value replacement for an existing key, missing-key KeyError behavior, and values equal to None. Accepted keys are nonnegative integers less than the prime p = 2⁶¹ − 1. At creation, parameters a ∈ {1,…,p−1} and b ∈ {0,…,p−1} are sampled; the bucket is h(k) = ((ak + b) mod p) mod m, where m is the current slot count. This is an affine universal-hashing-style family. The initial random parameters and bucket chains reduce dependence on any one regular key pattern, although the implementation is not intended for cryptographic security (Carter & Wegman, 1979).')
    para(doc,'Insertion scans the selected chain to update an existing key or appends a new entry. Search scans the matching chain and raises KeyError when the key is missing; deletion scans and removes the pair, then returns its old value. The implementation doubles its slot count when a new key would exceed the default load-factor threshold 0.75 and halves capacity when the load drops below 0.20, subject to the initial minimum. Each resize reinserts stored pairs into new buckets; resizing is occasional rather than a per-operation cost.')
    heading(doc,'Expected and Worst-Case Cost',2)
    para(doc,'Let n denote the number of stored pairs and m the number of buckets. The load factor α = n/m is the expected chain length under simple uniform hashing. A search (successful or unsuccessful) and deletion by key require expected Θ(1 + α) time because they may inspect a bucket chain. Updating an existing key has the same expected cost. Appending a new key has expected Θ(1 + α) cost in this implementation because duplicates are checked before insertion; with α kept at a constant threshold and geometric resizing, insertion is expected amortized Θ(1), including rehashing. Under adversarial collisions, a chain may grow to n entries and search, update, or deletion may require Θ(n). Storage is Θ(n + m). A universal hashing family reduces expected collisions over its random parameters but does not provide a deterministic constant-time guarantee.')
    heading(doc,'Load-Factor Management',2)
    para(doc,'Doubling capacity before α exceeds 0.75 limits expected search-chain growth while trading extra bucket-array memory for faster lookup. Lower thresholds may consume additional memory with modest benefit; higher thresholds save slots but generally increase collision work. A sustained low load factor also permits capacity reduction. Repeated resizing can affect latency, so real-time workloads may prefer scheduled growth or capacity planning.')
    heading(doc,'Hash Table Demonstration and Conclusions')
    caption(doc,'Table 2. Chaining outcomes for 3,000 inserted integer keys (one fixed seed)')
    rows=[]
    for r in hashes:
        rows.append((f'{float(r["threshold"]):.2f}',r['slots'],f'{float(r["load_factor"]):.4f}',r['collisions'],r['max_chain_length']))
    table(doc,['Growth threshold','Slots','Final α','Extra entries in chains','Longest chain'],rows,[1.25,0.8,0.85,1.65,1.35])
    para(doc,'The demonstration inserts and retrieves 3,000 integers while varying the maximum allowed load factor. At threshold 2.00, fewer buckets were allocated and longer chains appeared than at the stricter thresholds. The thresholds 0.50 and 0.75 happened to produce the same reported collision count for this one key sequence and hash seed; it would be incorrect to conclude that those settings always have identical collision behavior. Additional trials with different random hash parameters would improve the reliability of this comparison.')
    heading(doc,'Validation, Limitations, and Practical Implications',2)
    para(doc,'Automated tests cover empty, sorted, reverse-ordered, duplicate, and negative-value arrays, as well as different random seeds and large inputs. Hash-table tests verify collisions, resizing, invalid keys, updates, deletion, and 1,200 operations checked against Python’s dictionary. Tests support confidence but do not prove correctness for every input. Only integer keys are accepted; deployment would require concurrency controls and stronger security.')
    para(doc,'For infrastructure automation, randomized sorting could organize events, while chaining could index server identifiers. Random pivots improve expected scalability but cannot guarantee fast worst-case execution. A resized hash table provides expected fast lookups at the cost of extra buckets; universal-style hashing does not replace access controls or denial-of-service protections.')
    para(doc,'To reproduce the tables and chart, rerun benchmark.py and hash_load_experiment.py, then generate_report.py. Repository: https://github.com/nhuz44/MSCS532_Assignment3.')
    new_page(doc)
    heading(doc,'References')
    refs=[
       'Bentley, J. L., & McIlroy, M. D. (1993). Engineering a sort function. Software: Practice and Experience, 23(11), 1249–1265. https://doi.org/10.1002/spe.4380231105',
       'Carter, J. L., & Wegman, M. N. (1979). Universal classes of hash functions. Journal of Computer and System Sciences, 18(2), 143–154. https://doi.org/10.1016/0022-0000(79)90044-8',
       'Sedgewick, R. (1978). Implementing Quicksort programs. Communications of the ACM, 21(10), 847–857. https://doi.org/10.1145/359619.359631',
       'Massachusetts Institute of Technology. (2015). Lecture 6: Randomized algorithms [Course notes]. MIT OpenCourseWare. https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/',
    ]
    for s in refs:
        p=para(doc,s)
        p.paragraph_format.left_indent=Inches(.5)
        p.paragraph_format.first_line_indent=Inches(-.5)
    output=ROOT/'Assignment3_Report.docx'
    doc.save(output)
    print('Generated',output)


if __name__=='__main__':
    generate()
