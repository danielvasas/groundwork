import pytest


def test_signal_registration(basicApp):
    plugin = basicApp.plugins.get("BasicPlugin")
    signals = plugin.signals.get()
    assert len(signals.keys()) == 1
    assert "test" in signals.keys()


def test_signal_send(basicApp):
    answers = basicApp.signals.send("test", basicApp, text="test")
    assert len(answers) == 1
    assert isinstance(answers, list)
    assert len(answers[0]) == 2
    assert isinstance(answers[0], tuple)
    assert answers[0][1] == {'text': 'test'}


def test_signal_connect(basicApp):
    def _test_command(plugin, **kwargs):
        return "12345"

    plugin = basicApp.plugins.get("BasicPlugin")
    plugin.signals.connect("12345 receiver", "test", _test_command, "receiver 12345 for test")
    answers = plugin.signals.send("test")
    assert len(answers) == 2
    for answer in answers:
        if answer[0] == _test_command:
            assert answer[1] == "12345"


def test_signal_disconnect(basicApp):
    def _test_command(plugin, **kwargs):
        return "12345"

    plugin = basicApp.plugins.get("BasicPlugin")
    plugin.signals.connect("12345 receiver", "test", _test_command, "receiver 12345 for test")
    answers = plugin.signals.send("test")
    assert len(answers) == 2
    for answer in answers:
        if answer[0] == _test_command:
            assert answer[1] == "12345"

    plugin.signals.disconnect("12345 receiver")
    answers = plugin.signals.send("test")
    assert len(answers) == 1


def test_receiver_get(basicApp):
    def _test_command(plugin, **kwargs):
        return "12345"

    plugin = basicApp.plugins.get("BasicPlugin")
    receivers = plugin.signals.get_receiver()
    assert len(receivers) == 1  # test receiver
    plugin.signals.connect("12345 receiver", "test", _test_command, "receiver 12345 for test")
    receivers = plugin.signals.get_receiver()
    assert len(receivers) == 2
    plugin.deactivate()
    receivers = plugin.signals.get_receiver()
    assert len(receivers) == 0


def test_multi_plugin_deactivations(basicApp, EmptyPlugin):
    def test():
        pass

    plugin = basicApp.plugins.get("BasicPlugin")
    plugin2 = EmptyPlugin(app=basicApp, name="EmptyPlugin")
    plugin2.activate()
    assert plugin2.active is True

    plugin2.signals.register("test123", "test123 description")
    plugin2_signals = plugin2.signals.get()
    assert len(plugin2_signals) == 1

    plugin_signals = plugin.signals.get()
    # BasicPlugin has already registered a signal during init
    assert len(plugin_signals) == 1

    plugin2.deactivate()
    plugin2_signals = plugin2.signals.get()
    assert len(plugin2_signals) == 0
    assert plugin2.active is False

    assert len(plugin_signals) == 1
    assert plugin.active is True


def test_signal_handling(basicApp, EmptyPlugin):
    from blinker import NamedSignal
    from groundwork.signals import UnknownSignal

    def sig_reg_test(plugin, **kwargs):
        return ["data_1", "data_2"]

    plugin1 = EmptyPlugin(app=basicApp, name="EmptyPlugin")

    # This creates a gw receiver and a blinker internal signal called "test"
    plugin1.signals.connect("sig_reg_receiver", "sig_reg_test", sig_reg_test, "receiver sig_reg for test")

    # Check the blinker internal registration
    signal_namespace = basicApp.signals._namespace
    assert "sig_reg_test" in signal_namespace.keys()
    test_signal = signal_namespace["sig_reg_test"]
    assert isinstance(test_signal, NamedSignal)

    # Check the gw registration
    plugin_signals = plugin1.signals.get()
    # This must be 0, because gw has not registered a signal, this was done in blinker only
    assert len(plugin_signals) == 0

    app_signals = basicApp.signals.get()
    assert "sig_reg_test" not in app_signals.keys()

    # Check if signal sending throws an error (without a registered gw signal)
    with pytest.raises(UnknownSignal):
        plugin1.signals.send("sig_reg_test")

    # Check if gw has a registered receiver
    plugin_receivers = plugin1.signals.get_receiver()
    assert "sig_reg_receiver" in plugin_receivers.keys()

    # Register the missing gw signal
    plugin_signal = plugin1.signals.register("sig_reg_test", "signal for sig_reg_test")
    assert plugin_signal is not None

    # Recheck the gw registration
    plugin_signals = plugin1.signals.get()
    # This must be 1, because gw has registered a signal now
    assert len(plugin_signals) == 1

    # Sending should work now
    return_values = plugin1.signals.send("sig_reg_test")
    # Check if the receivers sends back needed data
    assert len(return_values) == 1
    assert return_values[0][1][0] == "data_1"


def test_signal_handling_via_plugins(basicApp, EmptyPlugin):
    def sig_reg_test_1(plugin, **kwargs):
        return ["data_1", "data_2"]

    def sig_reg_test_2(plugin, **kwargs):
        return ["data_3", "data_4"]

    plugin_send = EmptyPlugin(app=basicApp, name="Plugin_send")

    plugin_receive_pre = EmptyPlugin(app=basicApp, name="Plugin_receive_pre")
    plugin_receive_post = EmptyPlugin(app=basicApp, name="Plugin_receive_post")

    plugin_receive_pre.activate()
    plugin_receive_pre.signals.connect("sig_reg_pre_receiver", "signal_test",
                                       sig_reg_test_1, "receiver signal_test for test")

    plugin_send.activate()
    plugin_send.signals.register("signal_test", "signal_test doc")

    return_values = plugin_send.signals.send("signal_test")
    assert len(return_values) == 1

    plugin_receive_post.activate()
    plugin_receive_post.signals.connect("sig_reg_post_receiver", "signal_test",
                                        sig_reg_test_2, "receiver signal_test for test")

    return_values = plugin_send.signals.send("signal_test")
    assert len(return_values) == 2
