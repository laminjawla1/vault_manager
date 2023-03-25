document.addEventListener("DOMContentLoaded", function (event){
    let sc = document.createElement('script');
    sc.setAttribute('src', 'https://cdn.tiny.cloud/1/z2d7hsd3ewkd71wzzausnhpfnvm5acvqgwpsah9s3g2fuqtb/tinymce/6/tinymce.min.js');
    sc.setAttribute('referrerpolicy', 'origin')

    document.head.appendChild(sc);

    sc.onload = () => {
        const useDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const isSmallScreen = window.matchMedia('(max-width: 1023.5px)').matches;
        
        tinymce.init({
          selector: '#id_content',
          plugins: 'preview powerpaste casechange importcss tinydrive searchreplace autolink autosave save directionality advcode visualblocks visualchars fullscreen image link media mediaembed template codesample table charmap pagebreak nonbreaking anchor tableofcontents insertdatetime advlist lists checklist wordcount tinymcespellchecker a11ychecker editimage help formatpainter permanentpen pageembed charmap tinycomments mentions quickbars linkchecker emoticons advtable export footnotes mergetags autocorrect',
          mobile: {
            plugins: 'preview powerpaste casechange importcss tinydrive searchreplace autolink autosave save directionality advcode visualblocks visualchars fullscreen image link media mediaembed template codesample table charmap pagebreak nonbreaking anchor tableofcontents insertdatetime advlist lists checklist wordcount tinymcespellchecker a11ychecker help formatpainter pageembed charmap mentions quickbars linkchecker emoticons advtable footnotes mergetags autocorrect'
          },
          menu: {
            tc: {
              title: 'Comments',
              items: 'addcomment showcomments deleteallconversations'
            }
          },
          menubar: 'file edit view insert format tools table tc help',
          toolbar: 'undo redo | bold italic underline strikethrough | fontfamily fontsize blocks | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | a11ycheck ltr rtl | showcomments addcomment | footnotes | mergetags',
          toolbar_sticky: true,
          toolbar_sticky_offset: isSmallScreen ? 102 : 108,
          autosave_ask_before_unload: true,
          autosave_interval: '30s',
          autosave_prefix: '{path}{query}-{id}-',
          autosave_restore_when_empty: false,
          autosave_retention: '2m',
          image_advtab: true,
          link_list: [
            { title: 'My page 1', value: 'https://www.tiny.cloud' },
            { title: 'My page 2', value: 'http://www.moxiecode.com' }
          ],
          image_list: [
            { title: 'My page 1', value: 'https://www.tiny.cloud' },
            { title: 'My page 2', value: 'http://www.moxiecode.com' }
          ],
          image_class_list: [
            { title: 'None', value: '' },
            { title: 'Some class', value: 'class-name' }
          ],
          importcss_append: true,
          templates: [
            { title: 'New Table', description: 'creates a new table', content: '<div class="mceTmpl"><table width="98%%"  border="0" cellspacing="0" cellpadding="0"><tr><th scope="col"> </th><th scope="col"> </th></tr><tr><td> </td><td> </td></tr></table></div>' },
            { title: 'Starting my story', description: 'A cure for writers block', content: 'Once upon a time...' },
            { title: 'New list with dates', description: 'New List with dates', content: '<div class="mceTmpl"><span class="cdate">cdate</span><br><span class="mdate">mdate</span><h2>My List</h2><ul><li></li><li></li></ul></div>' }
          ],
          template_cdate_format: '[Date Created (CDATE): %m/%d/%Y : %H:%M:%S]',
          template_mdate_format: '[Date Modified (MDATE): %m/%d/%Y : %H:%M:%S]',
          height: 600,
          image_caption: true,
          quickbars_selection_toolbar: 'bold italic | quicklink h2 h3 blockquote quickimage quicktable',
          noneditable_class: 'mceNonEditable',
          toolbar_mode: 'sliding',
          spellchecker_ignore_list: ['Ephox', 'Moxiecode'],
          tinycomments_mode: 'embedded',
          content_style: '.mymention{ color: gray; }',
          contextmenu: 'link image editimage table configurepermanentpen',
          a11y_advanced_options: true,
          skin: useDarkMode ? 'oxide-dark' : 'oxide',
          content_css: useDarkMode ? 'dark' : 'default',
       
          autocorrect_capitalize: true,
          mergetags_list: [
            {
              title: 'Client',
              menu: [
                {
                  value: 'Client.LastCallDate',
                  title: 'Call date'
                },
                {
                  value: 'Client.Name',
                  title: 'Client name'
                }
              ]
            },
            {
              title: 'Proposal',
              menu: [
                {
                  value: 'Proposal.SubmissionDate',
                  title: 'Submission date'
                }
              ]
            },
            {
              value: 'Consultant',
              title: 'Consultant'
            },
            {
              value: 'Salutation',
              title: 'Salutation'
            }
          ]
        });
    }
});
