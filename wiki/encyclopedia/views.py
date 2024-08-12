from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from . import util
import random
import re

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    """Render the file"""
    entry_content = util.get_entry(title)
    if entry_content is None:
        # Raise an error message
        messages.error(request, 'Page not Found.')
        return HttpResponseRedirect(reverse('index'))
    # Convert .md to html
    html_content = markdown_to_html(entry_content)
    return render(request, 'encyclopedia/entry.html', {
        'title': title,
        'content': html_content
    })


def search(request):
    """Search all the files"""
    # Get the value of input field
    query = request.GET.get('q', '')
    all_entries = util.list_entries()
    for item in all_entries:
        if query.lower() == item.lower():
            # Render the appropriate page
            return entry(request, item)

    # If no page found show a search result
    results = [entry for entry in util.list_entries() if query.lower() in entry.lower()]
    return render(request, 'encyclopedia/search_results.html', {
        'query': query,
        'results': results
    })


def create(request):
    """Create new pages"""
    if request.method == 'POST':
        title = request.POST.get('title')
        # Check if the same title exists
        entries = util.list_entries()
        for entry in entries:
            if title.lower() == entry.lower():
                # Raise an error message
                messages.error(request, 'A page with this title already exists.')
                return HttpResponseRedirect(reverse('index'))
        content = request.POST.get('content')
        # Save the new page using utility functions
        util.save_entry(title, content)
        return redirect('entry', title=title)
    else:
        return render(request, 'encyclopedia/create.html')
    

def edit(request, title):
    """Edit pages"""
    if request.method == 'POST':
        content = request.POST.get('content')
        util.save_entry(title, content)
        return redirect('entry', title=title)
    else:
        content = util.get_entry(title)
        return render(request, 'encyclopedia/edit.html', {
            'title': title,
            'content': content
        })
    

def random_page(request):
    """Go to random page"""
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return redirect('entry', title=random_entry)


def markdown_to_html(content):
    """Convert .md to HTML"""
    lines = content.split('\n')
    in_ol = False
    in_ul = False
    for j in range(len(lines)):
        for i in range(6, 0, -1):
            if lines[j].startswith('#' * i + ' '):
                lines[j] = f'<h{i}>' + lines[j][i+1:] + f'</h{i}>'
                break
        else:
            # Numbered lists
            if re.match(r'^\d+\. ', lines[j]):
                if not in_ol:
                    lines[j] = '<ol>' + f'<li>{lines[j][lines[j].index(" ") + 1:]}</li>'
                    in_ol = True
                else:
                    lines[j] = f'<li>{lines[j][lines[j].index(" ") + 1:]}</li>'
            else:
                if in_ol:
                    lines[j-1] += '</ol>'
                    in_ol = False

            # Bullet lists
            if re.match(r'^[\*\-\+] ', lines[j]):
                if not in_ul:
                    lines[j] = '<ul>' + f'<li>{lines[j][2:]}</li>'
                    in_ul = True
                else:
                    lines[j] = f'<li>{lines[j][2:]}</li>'
            else:
                if in_ul:
                    lines[j-1] += '</ul>'
                    in_ul = False

            # Paragraphs
                elif lines[j].strip():  # Check if the line is not empty
                    lines[j] = f'<p>{lines[j]}</p>'
        
        # Bold text
        lines[j] = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', lines[j])
        # Italic text
        lines[j] = re.sub(r'\*(.*?)\*', r'<i>\1</i>', lines[j])

    if in_ol:
        lines[-1] += '</ol>'
    if in_ul:
        lines[-1] += '</ul>'
    
    # Join lines into a single string
    content = '\n'.join(lines)

    # Links
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)

    return content