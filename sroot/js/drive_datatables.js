$(document).ready(function drive_table() {
    var table = $('#drive-table').DataTable({
        // ...
        "dom": '<"top"lBf>rt<"bottom"ip><"clear">',
        buttons: [
            {
                extend: 'copy',
                exportOptions: {
                    columns: ':visible'
                }
            },
            {
                extend: 'excel',
                exportOptions: {
                    columns: ':visible'
                }
            },
            {
                extend: 'print',
                exportOptions: {
                    columns: ':visible'
                }
            },
            {
                extend: 'pdf',
                exportOptions: {
                    columns: ':visible'
                }
            },

            'colvis'
        ],
        "processing": true,
        "serverSide": true,
        "ajax": {
            'url': '/view-drive-dt',
                },
        // 'displayStart': (page-1)*page_length,
        "stateSave": true,
        'initComplete': function() {
            table.page.info().page;
        },
        "columnDefs": [
                        {"orderable": true , "targets": 0},
                        {"orderable": true , "targets": 1},
                        {"orderable": true , "targets": 2},
                        {"orderable": true , "targets": 3},
                        {"orderable": true , "targets": 4},
                        {"orderable": true , "targets": 5},
                        {
                            "orderable": true , "targets": 6,
                            "render": function(data,type,row,meta){
                                return '<a href="'+row[6]+'">Edit</a>';
                            }
                        },
                        {
                            "orderable": true , "targets": 7,
                            "render": function(data,type,row,meta){
                                return '<a href="'+row[7]+'">Delete</a>';
                            }
                        },
                    ]
        // ...
        });
    });
