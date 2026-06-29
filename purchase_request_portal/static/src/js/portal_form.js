/* Purchase Request Portal Form JavaScript */
(function() {
    'use strict';

    var lineCounter = 0;

    // Function to add a new line
    function addLine() {
        var lineIndex = lineCounter;
        lineCounter++;

        // Get UOM options from template
        var uomOptions = $('#uom_template').html() || '<option value="">Select UoM...</option>';

        var lineHtml = `
            <div class="card mb-3 request-line-item">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-5">
                            <div class="form-group">
                                <label for="line_name_${lineIndex}">Product/Description <span class="text-danger">*</span></label>
                                <input type="text" name="line_name_${lineIndex}" id="line_name_${lineIndex}"
                                       class="form-control" required="required" placeholder="Ingrese descripcion o producto"/>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="line_qty_${lineIndex}">Quantity <span class="text-danger">*</span></label>
                                <input type="number" name="line_qty_${lineIndex}" id="line_qty_${lineIndex}"
                                       class="form-control" required="required" min="0.01" step="0.01" value="1.00"/>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="line_uom_${lineIndex}">UoM <span class="text-danger">*</span></label>
                                <select name="line_uom_${lineIndex}" id="line_uom_${lineIndex}"
                                        class="form-control uom-select" required="required">
                                    ${uomOptions}
                                </select>
                            </div>
                        </div>
                        <div class="col-md-1 d-flex align-items-center">
                            <button type="button" class="btn btn-danger btn-sm remove_line_btn mt-3">
                                <i class="fa fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        $('#request_lines_container').append(lineHtml);
    }

    // Function to handle department change - filter employees based on data attribute
    function onDepartmentChange() {
        var departmentId = $('#department_id').val();
        var $employeeSelect = $('#employee_id');

        if (!departmentId) {
            // If no department selected, hide all employees
            $employeeSelect.find('option').each(function() {
                if ($(this).val() !== '') {
                    $(this).hide();
                }
            });
            $employeeSelect.val('');
            return;
        }

        // Loop through each option in the employee select
        $employeeSelect.find('option').each(function() {
            var $option = $(this);

            // Skip the placeholder option
            if ($option.val() === '') {
                $option.show();
                return;
            }

            // Get the department ID of the employee option
            var employeeDepartmentId = $option.attr('data-department-id');

            // Show or hide the option based on whether it matches the selected department ID
            if (employeeDepartmentId === departmentId) {
                $option.show();
            } else {
                $option.hide();
            }
        });

        // Reset the employee select value
        $employeeSelect.val('');

        console.log('Department changed to:', departmentId);
    }

    // Initialize when document is ready
    $(document).ready(function() {
        console.log('Purchase Request Portal - JavaScript Loaded');

        // Add first line by default
        addLine();

        // Department change handler
        $(document).on('change', '#department_id', onDepartmentChange);

        // Add line button handler
        $(document).on('click', '#add_line_btn', function(e) {
            e.preventDefault();
            addLine();
            console.log('Line added, total lines:', lineCounter);
        });

        // Remove line button handler (using event delegation)
        $(document).on('click', '.remove_line_btn', function(e) {
            e.preventDefault();
            $(this).closest('.request-line-item').remove();
            console.log('Line removed');
        });

        // Run the filter function initially to hide all employees until department is selected
        onDepartmentChange();
    });

})();
