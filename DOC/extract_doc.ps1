$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open('s:\Sahara_AI\Sahara_ai_Project_Document.docx')
$text = $doc.Content.Text
$doc.Close(0)
$word.Quit()
[System.IO.File]::WriteAllText('s:\Sahara_AI\doc_content.txt', $text, [System.Text.Encoding]::UTF8)
Write-Host "Done - text extracted"
